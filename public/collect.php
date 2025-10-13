<?php
// Sem MVC. Único handler do POST.
// Requisitos: PHP com ZipArchive habilitado; Python 3.11; Playwright instalado.

ini_set('display_errors', 0);
error_reporting(E_ALL);

function guidv4() {
  // GUID simples
  $data = random_bytes(16);
  $data[6] = chr(ord($data[6]) & 0x0f | 0x40);
  $data[8] = chr(ord($data[8]) & 0x3f | 0x80);
  return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
}

$base = realpath(__DIR__ . '/../');
$storage = $base . '/storage';
if (!is_dir($storage)) { mkdir($storage, 0775, true); }

$url = isset($_POST['url']) ? trim($_POST['url']) : '';
if (!$url || !filter_var($url, FILTER_VALIDATE_URL)) {
  http_response_code(400);
  echo "URL inválida.";
  exit;
}

$clientIp = $_SERVER['REMOTE_ADDR'] ?? null;
$clientUa  = $_SERVER['HTTP_USER_AGENT'] ?? null;

$runId = guidv4();
$outDir = $storage . '/' . $runId;
mkdir($outDir, 0775, true);

// Chama o worker Python
$py = escapeshellcmd($base . '/worker/.venv/bin/python3');
$script = escapeshellarg($base . '/worker/collector.py');
$env_path = escapeshellarg('/var/www/.cache/ms-playwright');
$cmd = 'PLAYWRIGHT_BROWSERS_PATH=' . $env_path . ' ' . $py . ' ' . $script
    . ' --url ' . escapeshellarg($url)
    . ' --outdir ' . escapeshellarg($outDir)
    . ' --request_ip ' . escapeshellarg($clientIp ?? '')
    . ' --request_ua ' . escapeshellarg($clientUa ?? '');

exec($cmd . ' 2>&1', $output, $ret);
if ($ret !== 0) {
  file_put_contents($outDir . '/error.log', implode("\n", $output));
  http_response_code(500);
  echo "Falha ao coletar. Consulte o log.";
  exit;
}

// Compacta em ZIP
$zipPath = $outDir . '/traceguard_' . $runId . '.zip';
$zip = new ZipArchive();
if ($zip->open($zipPath, ZipArchive::CREATE)!==TRUE) {
  http_response_code(500);
  echo "Falha ao criar ZIP.";
  exit;
}
$files = scandir($outDir);
foreach ($files as $f) {
  if ($f === '.' || $f === '..') continue;
  if (substr($f, -4) === '.zip') continue;
  $zip->addFile($outDir . '/' . $f, $f);
}
$zip->close();

// Redireciona para página de download
header('Location: download.php?id=' . urlencode($runId));