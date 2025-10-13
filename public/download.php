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
<body>
<header><h1>TraceGuard</h1></header>
<main>
  <div class="card">
    <p>Coleta concluída. Baixe o pacote completo (ZIP) e consulte o manifest/hashes:</p>
    <p><a href="<?php echo './file.php?f=' . urlencode(basename($zipFile)) . '&id=' . urlencode($runId); ?>">⬇️ Baixar ZIP</a></p>
    <p><a href="<?php echo './file.php?f=manifest.json&id=' . urlencode($runId); ?>">🔎 Ver manifest.json</a></p>
    <p><a href="<?php echo './file.php?f=hashes.json&id=' . urlencode($runId); ?>">🔐 Ver hashes.json</a></p>
    <p class="small">Guarde o ZIP inteiro para preservar a cadeia de custódia.</p>
  </div>
</main>
</body>
</html>