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
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>TraceGuard – Download</title>
  <link href="./style.css" rel="stylesheet">
</head>
<body style="color: #333;">
<header>
  <div style="display: flex; justify-content: center; align-items: center;">
    <img src="../logo.png" alt="TraceGuard Logo" style="height: 50px; width: auto;">
  </div>
</header>
<main>
  <div class="card">
    <h2 style="color: white;">✅ Coleta Concluída com Sucesso!</h2>
    <p style="color: white;">Todos os artefatos foram coletados e estão disponíveis para download:</p>

    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
      <h3>📋 Downloads Disponíveis:</h3>
      <p><a href="<?php echo './file.php?f=' . urlencode(basename($zipFile)) . '&id=' . urlencode($runId); ?>" target="_blank" style="background: #28a745; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold;">⬇️ Baixar ZIP Completo</a></p>

      <p><a href="<?php echo './file.php?f=relatorio_traceguard.pdf&id=' . urlencode($runId); ?>" target="_blank" style="background: #dc3545; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold;">📄 Baixar Relatório PDF</a></p>
    </div>

    <div style="background: #e9ecef; color: #000; padding: 15px; border-radius: 8px; margin: 15px 0;">
      <h4 style="color: #007bff; margin-bottom: 10px;">🔍 Arquivos Individuais:</h4>
      <p style="color: #000; margin: 8px 0;"><a href="<?php echo './file.php?f=manifest.json&id=' . urlencode($runId); ?>" target="_blank">📋 Ver manifest.json</a></p>
      <p style="color: #000; margin: 8px 0;"><a href="<?php echo './file.php?f=hashes.json&id=' . urlencode($runId); ?>" target="_blank">🔐 Ver hashes.json</a></p>
      <p style="color: #000; margin: 8px 0;"><a href="<?php echo './file.php?f=screenshot.png&id=' . urlencode($runId); ?>" target="_blank">🖼️ Ver screenshot</a></p>
    </div>

    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 15px 0;">
      <h4>⚠️ Importante:</h4>
      <p class="small">Guarde o ZIP inteiro para preservar a cadeia de custódia. O relatório PDF contém todas as informações organizadas para uso jurídico.</p>
    </div>
  </div>
</main>
<footer style="text-align: center; margin-top: 40px; padding: 20px; background: linear-gradient(135deg, #2c3e50, #34495e); color: white; border-radius: 10px;">
  <p style="margin: 0; font-size: 1.1em; font-weight: bold;">
    TraceGuard 2025 - by <a href="https://instagram.com/peritosegurancadainformacao" target="_blank" style="color: #ffc107; text-decoration: none;">Osvaldo Janeri Filho</a> |
    <a href="https://www.linkedin.com/in/osvaldo-janeri-filho-66794114" target="_blank" style="color: #0077b5; text-decoration: none;">LinkedIn</a> |
    <a href="https://github.com/ojaneri/traceguard" target="_blank" style="color: #fff; text-decoration: none;">GitHub</a>
  </p>
</footer>
</body>
</html>