#!/usr/bin/env python3
import argparse, json, hashlib, socket, ssl, datetime, os, base64, re
from pathlib import Path
import httpx, whois, dns.resolver
from playwright.sync_api import sync_playwright
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def tls_info(host: str, port=443):
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert_bin = ssock.getpeercert(True)
            cert = ssl.DER_cert_to_PEM_cert(cert_bin)
            return {
                "tls_version": ssock.version(),
                "cipher": ssock.cipher(),
                "peer_cert_pem": cert,
            }

def dns_info(host: str):
    out = {}
    r = dns.resolver.Resolver()
    for rr in ["A", "AAAA", "NS", "MX", "TXT"]:
        try:
            answers = r.resolve(host, rr)
            out[rr] = [a.to_text() for a in answers]
        except Exception:
            out[rr] = []
    return out

def http_headers(url: str):
    with httpx.Client(follow_redirects=True, timeout=20) as client:
        resp = client.get(url)
        return {
            "final_url": str(resp.url),
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
        }

def take_screenshot(url: str, out_png: Path, width=1366, height=768):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": width, "height": height})
        page = ctx.new_page()
        page.goto(url, wait_until="load", timeout=30000)
        page.screenshot(path=str(out_png), full_page=True)
        # opcional: salvar HTML
        html = page.content()
        return {"html_len": len(html)}

def write_json(p: Path, data: dict):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def render_template(template_path: Path, data: dict) -> str:
    """Renderiza template HTML com os dados coletados"""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Função auxiliar para verificar igualdade
    def eq(a, b):
        return a == b

    # Função auxiliar para obter tamanho
    def length(s):
        return len(str(s))

    # Adiciona funções ao ambiente de dados
    data['eq'] = eq
    data['length'] = length

    # Processa template simples (substituição de variáveis)
    for key, value in data.items():
        if isinstance(value, dict):
            # Trata dicionários especiais (headers, whois, etc.)
            for dict_key, dict_value in value.items():
                template = re.sub(
                    r'\{\{#each ' + re.escape(key) + r'\}\}(.*?)\{\{\/each\}\}',
                    lambda m, k=dict_key, v=dict_value: process_each_section(m.group(1), {k: v}),
                    template,
                    flags=re.DOTALL
                )
        elif isinstance(value, list):
            # Trata listas
            template = re.sub(
                r'\{\{#each ' + re.escape(key) + r'\}\}(.*?)\{\{\/each\}\}',
                lambda m, items=value: process_each_list(m.group(1), items),
                template,
                flags=re.DOTALL
            )
        else:
            # Substituição simples
            template = template.replace(f'{{{{{key}}}}}', str(value))

    return template

def process_each_section(template_section: str, data: dict) -> str:
    """Processa seções {{#each dict}}"""
    result = []
    for key, value in data.items():
        # Substitui {{@key}} e {{this}}
        section = template_section.replace('{{@key}}', str(key))
        section = section.replace('{{this}}', str(value))
        result.append(section)
    return ''.join(result)

def process_each_list(template_section: str, items: list) -> str:
    """Processa seções {{#each list}}"""
    if not items:
        return "Nenhum item encontrado"

    result = []
    for i, item in enumerate(items):
        # Substitui {{this}} e verifica se é o último item
        section = template_section.replace('{{this}}', str(item))
        section = section.replace('{{#unless @last}}', '' if i == len(items) - 1 else '')
        section = section.replace('{{/unless}}', '' if i == len(items) - 1 else '')
        result.append(section)
    return ''.join(result)

def generate_pdf_report(outdir: Path, data: dict, screenshot_path: Path):
    """Gera relatório PDF profissional usando ReportLab"""
    pdf_path = outdir / 'relatorio_traceguard.pdf'

    # Cria o documento PDF
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.gray
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkgreen,
        borderColor=colors.darkgreen,
        borderWidth=0,
        borderPadding=5
    )

    # Logo
    try:
        logo_path = Path(__file__).parent.parent / 'logo.png'
        if logo_path.exists():
            # Mantém proporções originais com altura menor
            logo = Image(str(logo_path), height=1.5*cm)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 15))
    except Exception as e:
        pass  # Continua sem logo se houver erro

    # Cabeçalho
    story.append(Paragraph("RELATÓRIO DE ANÁLISE DIGITAL", title_style))
    story.append(Paragraph("TraceGuard - Sistema de Coleta de Evidências Digitais", subtitle_style))
    story.append(Spacer(1, 20))

    # Informações do caso
    story.append(Paragraph("INFORMAÇÕES DO CASO", section_style))

    case_data = [
        ['URL Solicitada:', data.get('requested_url', 'N/A')],
        ['URL Final:', data.get('final_url', 'N/A')],
        ['Timestamp (UTC):', data.get('timestamp_utc', 'N/A')],
        ['IP do Solicitante:', data.get('requester_ip', 'N/A')],
        ['User-Agent:', data.get('requester_ua', 'N/A')[:100] + '...' if len(data.get('requester_ua', '')) > 100 else data.get('requester_ua', 'N/A')],
    ]

    case_table = Table(case_data, colWidths=[3*cm, 12*cm])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('WORDWRAP', (0, 0), (-1, -1), 'CJK')  # Habilita quebra de linha
    ]))
    story.append(case_table)
    story.append(Spacer(1, 20))

    # Screenshot
    if screenshot_path.exists():
        try:
            # Mantém proporções originais do screenshot (16:9)
            from PIL import Image as PILImage
            with PILImage.open(str(screenshot_path)) as img:
                width, height = img.size
                aspect_ratio = width / height

            # Calcula largura baseada na altura desejada mantendo proporções
            target_height = 12*cm
            target_width = target_height * aspect_ratio

            # Se a largura for muito grande, ajusta
            max_width = 16*cm
            if target_width > max_width:
                target_width = max_width
                target_height = target_width / aspect_ratio

            screenshot_img = Image(str(screenshot_path), width=target_width, height=target_height)
            screenshot_img.hAlign = 'CENTER'
            story.append(Paragraph("CAPTURA DE TELA", section_style))
            story.append(screenshot_img)
            story.append(Spacer(1, 20))
        except Exception as e:
            story.append(Paragraph(f"Erro ao carregar screenshot: {str(e)}", styles['Normal']))

    # Headers HTTP
    story.append(Paragraph("HEADERS HTTP", section_style))
    headers = data.get('http_headers', {})
    if headers:
        header_data = [['Campo', 'Valor']] + [[k, str(v)[:200] + '...' if len(str(v)) > 200 else str(v)] for k, v in headers.items()]
        header_table = Table(header_data, colWidths=[4*cm, 10*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK')  # Habilita quebra de linha
        ]))
        story.append(header_table)
    else:
        story.append(Paragraph("Nenhum header HTTP disponível", styles['Normal']))
    story.append(Spacer(1, 20))

    # WHOIS
    story.append(Paragraph("INFORMAÇÕES WHOIS", section_style))
    whois_data = data.get('whois_data', {})
    if 'error' not in whois_data:
        whois_items = [[k, str(v)[:200] + '...' if len(str(v)) > 200 else str(v)] for k, v in whois_data.items()]
        if whois_items:
            whois_table = Table([['Propriedade', 'Valor']] + whois_items, colWidths=[4*cm, 10*cm])
            whois_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), 'CJK')  # Habilita quebra de linha
            ]))
            story.append(whois_table)
        else:
            story.append(Paragraph("Nenhum dado WHOIS disponível", styles['Normal']))
    else:
        story.append(Paragraph(f"Erro WHOIS: {whois_data['error']}", styles['Normal']))
    story.append(Spacer(1, 20))

    # DNS
    story.append(Paragraph("REGISTROS DNS", section_style))
    dns_data = data.get('dns_data', {})
    dns_items = []
    for record_type, records in dns_data.items():
        if records:
            dns_items.append([record_type, ', '.join(records)])

    if dns_items:
        dns_table = Table([['Tipo', 'Registros']] + dns_items, colWidths=[3*cm, 11*cm])
        dns_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK')  # Habilita quebra de linha
        ]))
        story.append(dns_table)
    else:
        story.append(Paragraph("Nenhum registro DNS disponível", styles['Normal']))
    story.append(Spacer(1, 20))

    # Hashes
    story.append(Paragraph("HASHES DE VERIFICAÇÃO (SHA-256)", section_style))
    hashes = data.get('hashes', {})
    hash_items = [[k, v] for k, v in hashes.items() if v]

    if hash_items:
        hash_table = Table([['Arquivo', 'Hash SHA-256']] + hash_items, colWidths=[4*cm, 11*cm])
        hash_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK')  # Habilita quebra de linha
        ]))
        story.append(hash_table)
    else:
        story.append(Paragraph("Nenhum hash disponível", styles['Normal']))
    story.append(Spacer(1, 20))

    # Rodapé com créditos
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceBefore=30
    )

    story.append(Paragraph("=" * 60, footer_style))
    story.append(Paragraph("TraceGuard 2025 - Sistema de Coleta de Evidências Digitais", footer_style))
    story.append(Paragraph("Desenvolvido por Osvaldo Janeri Filho", footer_style))
    story.append(Paragraph(f"Relatório gerado em: {data.get('timestamp_utc', 'N/A')}", footer_style))
    story.append(Paragraph("Este documento possui valor probatório para fins jurídicos.", footer_style))

    # Gera o PDF
    doc.build(story)

    return pdf_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--request_ip", default=None)
    ap.add_argument("--request_ua", default=None)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) Timestamp e identificação
    ts_iso = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    # 2) HEADERS HTTP do destino
    headers_obj = http_headers(args.url)
    write_json(outdir / "http_headers.json", headers_obj)

    # 3) Screenshot
    screenshot_png = outdir / "screenshot.png"
    nav_info = take_screenshot(headers_obj["final_url"], screenshot_png)

    # 4) WHOIS / DNS / TLS
    host = socket.getfqdn(httpx.URL(headers_obj["final_url"]).host)
    whois_data = {}
    try:
        whois_data = whois.whois(host)
        whois_data = {k: (str(v) if not isinstance(v, (str, int, float, dict, list)) else v)
                      for k, v in whois_data.__dict__.items()}
    except Exception as e:
        whois_data = {"error": str(e)}

    dns_data = dns_info(host)
    tls_data = {}
    try:
        tls_data = tls_info(host)
    except Exception as e:
        tls_data = {"error": str(e)}

    write_json(outdir / "whois.json", whois_data)
    write_json(outdir / "dns.json", dns_data)
    write_json(outdir / "tls.json", tls_data)

    # 5) Hashes
    hashes = {
        "screenshot.png": sha256_file(screenshot_png) if screenshot_png.exists() else None,
        "http_headers.json": sha256_file(outdir / "http_headers.json"),
        "whois.json": sha256_file(outdir / "whois.json"),
        "dns.json": sha256_file(outdir / "dns.json"),
        "tls.json": sha256_file(outdir / "tls.json"),
    }
    write_json(outdir / "hashes.json", hashes)

    # 6) Manifest (cadeia de custódia)
    manifest = {
        "tool": "TraceGuard",
        "version": "0.1.0",
        "timestamp_utc": ts_iso,
        "requested_url": args.url,
        "final_url": headers_obj.get("final_url"),
        "requester": {
            "ip": args.request_ip,
            "user_agent": args.request_ua
        },
        "artifacts": {
            "screenshot": "screenshot.png",
            "http_headers": "http_headers.json",
            "whois": "whois.json",
            "dns": "dns.json",
            "tls": "tls.json",
            "hashes": "hashes.json",
            "legal_report": "relatorio_traceguard.pdf"
        },
        "notes": {
            "html_captured": False,
            "nav_html_len": nav_info.get("html_len"),
        }
    }
    write_json(outdir / "manifest.json", manifest)

    # 7) Gera relatório jurídico em PDF
    report_data = {
        "tool": "TraceGuard",
        "version": "0.1.0",
        "timestamp_utc": ts_iso,
        "requested_url": args.url,
        "final_url": headers_obj.get("final_url"),
        "requester_ip": args.request_ip or "N/A",
        "requester_ua": args.request_ua or "N/A",
        "http_headers": headers_obj.get("headers", {}),
        "whois_data": whois_data,
        "whois_error": whois_data.get("error") if "error" in whois_data else None,
        "dns_data": dns_data,
        "tls_data": tls_data,
        "tls_error": tls_data.get("error") if "error" in tls_data else None,
        "hashes": hashes,
        "html_captured": False,
        "nav_html_len": nav_info.get("html_len"),
    }

    pdf_path = generate_pdf_report(outdir, report_data, screenshot_png)
    print(f"Relatório PDF gerado: {pdf_path}")

if __name__ == "__main__":
    main()