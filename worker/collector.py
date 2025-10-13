#!/usr/bin/env python3
import argparse, json, hashlib, socket, ssl, datetime, os, base64
from pathlib import Path
import httpx, whois, dns.resolver
from playwright.sync_api import sync_playwright

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
            "hashes": "hashes.json"
        },
        "notes": {
            "html_captured": False,
            "nav_html_len": nav_info.get("html_len"),
        }
    }
    write_json(outdir / "manifest.json", manifest)

if __name__ == "__main__":
    main()