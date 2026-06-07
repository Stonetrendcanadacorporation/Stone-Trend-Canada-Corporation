<?php
/**
 * Save site content JSON. POST body = raw JSON.
 * Writes to data/site-content.json. Create data/ and make it writable (chmod 755 or 775).
 * Usage: upload to GoDaddy; ensure PHP is enabled and data/ exists and is writable.
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if ($data === null && json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Invalid JSON']);
    exit;
}

$dir = __DIR__ . '/data';
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}
$file = $dir . '/site-content.json';

// Support per-page content: merge into existing JSON by page key
$page = isset($data['page']) ? preg_replace('/[^a-zA-Z0-9_\-\.]/', '', $data['page']) : 'index';
$existing = [];
if (file_exists($file)) {
    $existing = json_decode(file_get_contents($file), true) ?: [];
}
if (!is_array($existing)) {
    $existing = [];
}
$existing[$page] = $data;
if (file_put_contents($file, json_encode($existing, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)) === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Could not write file']);
    exit;
}

echo json_encode(['ok' => true]);
?>
