<?php
$base = realpath(__DIR__ . '/../');
$storage = $base . '/storage';
$runId = $_GET['id'] ?? '';
$file = $_GET['f'] ?? '';

$dir = realpath($storage . '/' . $runId);
if (!$dir || strpos($dir, realpath($storage)) !== 0) { http_response_code(404); exit; }

$path = realpath($dir . '/' . $file);
if (!$path || strpos($path, $dir) !== 0 || !file_exists($path)) { http_response_code(404); exit; }

$mime = mime_content_type($path);
header('Content-Type: ' . $mime);
header('Content-Disposition: inline; filename="' . basename($path) . '"');
readfile($path);