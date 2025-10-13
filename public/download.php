<?php
$base = realpath(__DIR__ . '/../');
$storage = $base . '/storage';
$runId = $_GET['id'] ?? '';
$path = realpath($storage . '/' . $runId);

if (!$runId || !$path || strpos($path, realpath($storage)) !== 0) {
  http_response_code(404);
  echo "Coleta não encontrada.";
  exit;
}

$zip = glob($path . '/*.zip');
$zipFile = $zip ? $zip[0] : null;

if (!$zipFile || !file_exists($zipFile)) {
  http_response_code(404);
  echo "Arquivo ZIP não encontrado.";
  exit;
}

$manifest = $path . '/manifest.json';
$hashes = $path . '/hashes.json';

?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TraceGuard – Download</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, Segoe UI, Roboto, Arial, sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            min-height: 100vh;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        .header img {
            height: 80px;
            width: auto;
            margin-bottom: 15px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .card {
            background: #1f2937;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .success-message {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: #065f46;
            border-radius: 12px;
            border-left: 5px solid #10b981;
        }

        .success-message h2 {
            color: #10b981;
            font-size: 2em;
            margin-bottom: 15px;
        }

        .success-message p {
            color: #d1fae5;
            font-size: 1.1em;
        }

        .download-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }

        .download-section {
            background: #374151;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            border-top: 4px solid #3b82f6;
        }

        .download-section.primary {
            border-top-color: #10b981;
        }

        .download-section.secondary {
            border-top-color: #ef4444;
        }

        .download-section h3 {
            color: #60a5fa;
            margin-bottom: 20px;
            font-size: 1.4em;
        }

        .download-btn {
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1em;
            transition: all 0.3s ease;
            border: 2px solid #3b82f6;
            margin: 10px;
        }

        .download-btn:hover {
            background: #2563eb;
            border-color: #2563eb;
            transform: translateY(-2px);
        }

        .download-btn.primary {
            background: #10b981;
            border-color: #10b981;
        }

        .download-btn.primary:hover {
            background: #059669;
            border-color: #059669;
        }

        .download-btn.secondary {
            background: #ef4444;
            border-color: #ef4444;
        }

        .download-btn.secondary:hover {
            background: #dc2626;
            border-color: #dc2626;
        }

        .files-section {
            background: #374151;
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
        }

        .files-section h3 {
            color: #60a5fa;
            margin-bottom: 20px;
            font-size: 1.3em;
            text-align: center;
        }

        .files-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .file-item {
            background: #4b5563;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }

        .file-item a {
            color: #93c5fd;
            text-decoration: none;
            font-weight: 500;
            display: block;
            transition: color 0.3s ease;
        }

        .file-item a:hover {
            color: #60a5fa;
        }

        .warning-section {
            background: #374151;
            border: 2px solid #f59e0b;
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
            text-align: center;
        }

        .warning-section h3 {
            color: #fbbf24;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .warning-section p {
            color: #fef3c7;
            font-size: 1em;
        }

        .footer {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            text-align: center;
            padding: 30px;
            border-radius: 15px;
            margin-top: 40px;
        }

        .footer p {
            margin: 0;
            font-size: 1.1em;
            font-weight: bold;
        }

        .footer a {
            color: #ffc107;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .footer a:hover {
            color: white;
        }

        @media (max-width: 768px) {
            .download-grid {
                grid-template-columns: 1fr;
            }

            .files-list {
                grid-template-columns: 1fr;
            }

            .download-btn {
                display: block;
                margin: 10px 0;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="../logo.png" alt="TraceGuard Logo">
    </div>

    <div class="container">
        <div class="card">
            <div class="success-message">
                <h2>✅ Coleta Concluída com Sucesso!</h2>
                <p>Todos os artefatos foram coletados e estão disponíveis para download</p>
            </div>

            <div class="download-grid">
                <div class="download-section primary">
                    <h3>📦 Pacote Completo</h3>
                    <a href="<?php echo './file.php?f=' . urlencode(basename($zipFile)) . '&id=' . urlencode($runId); ?>" target="_blank" class="download-btn primary">
                        ⬇️ Baixar ZIP Completo
                    </a>
                </div>

                <div class="download-section secondary">
                    <h3>📋 Relatório Jurídico</h3>
                    <a href="<?php echo './file.php?f=relatorio_traceguard.pdf&id=' . urlencode($runId); ?>" target="_blank" class="download-btn secondary">
                        📄 Baixar PDF Profissional
                    </a>
                </div>
            </div>

            <div class="files-section">
                <h3>🔍 Arquivos Individuais</h3>
                <div class="files-list">
                    <div class="file-item">
                        <a href="<?php echo './file.php?f=manifest.json&id=' . urlencode($runId); ?>" target="_blank">📋 manifest.json</a>
                    </div>
                    <div class="file-item">
                        <a href="<?php echo './file.php?f=hashes.json&id=' . urlencode($runId); ?>" target="_blank">🔐 hashes.json</a>
                    </div>
                    <div class="file-item">
                        <a href="<?php echo './file.php?f=screenshot.png&id=' . urlencode($runId); ?>" target="_blank">🖼️ screenshot.png</a>
                    </div>
                </div>
            </div>

            <div class="warning-section">
                <h3>⚠️ Importante</h3>
                <p>Guarde o ZIP inteiro para preservar a cadeia de custódia. O relatório PDF contém todas as informações organizadas para uso jurídico.</p>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>
            TraceGuard 2025 - by <a href="https://instagram.com/peritosegurancadainformacao">Osvaldo Janeri Filho</a> |
            <a href="https://www.linkedin.com/in/osvaldo-janeri-filho-66794114">LinkedIn</a> |
            <a href="https://github.com/ojaneri/traceguard">GitHub</a>
        </p>
    </div>
</body>
</html>