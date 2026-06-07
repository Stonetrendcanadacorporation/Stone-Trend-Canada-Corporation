<?php
/**
 * Save site config (e.g. form email). POST: formEmail = address.
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

$file = __DIR__ . '/data/site-config.json';
$dir = dirname($file);
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}

$formEmail = isset($_POST['formEmail']) ? trim((string) $_POST['formEmail']) : '';
$contactInfo = isset($_POST['contactInfo']) ? $_POST['contactInfo'] : '';
if (is_string($contactInfo)) {
    $contactInfo = json_decode($contactInfo, true);
}
if (!is_array($contactInfo)) {
    $contactInfo = null;
}
$headerLogoUrl = isset($_POST['headerLogoUrl']) ? trim((string) $_POST['headerLogoUrl']) : null;
$smtpHost = isset($_POST['smtpHost']) ? trim((string) $_POST['smtpHost']) : null;
$smtpPort = isset($_POST['smtpPort']) ? trim((string) $_POST['smtpPort']) : null;
$smtpUser = isset($_POST['smtpUser']) ? trim((string) $_POST['smtpUser']) : null;
$smtpPass = isset($_POST['smtpPass']) ? (string) $_POST['smtpPass'] : null;
$smtpSecure = isset($_POST['smtpSecure']) ? trim((string) $_POST['smtpSecure']) : null;
$recoveryEmail = isset($_POST['recoveryEmail']) ? trim((string) $_POST['recoveryEmail']) : null;
$secondaryRecoveryEmail = isset($_POST['secondaryRecoveryEmail']) ? trim((string) $_POST['secondaryRecoveryEmail']) : null;
$recoveryAnswer1 = isset($_POST['recoveryAnswer1']) ? trim((string) $_POST['recoveryAnswer1']) : null;
$recoveryAnswer2 = isset($_POST['recoveryAnswer2']) ? trim((string) $_POST['recoveryAnswer2']) : null;
$recoveryAnswer3 = isset($_POST['recoveryAnswer3']) ? trim((string) $_POST['recoveryAnswer3']) : null;

$data = [];
if (file_exists($file)) {
    $data = json_decode(file_get_contents($file), true) ?: [];
}
if ($formEmail !== '' && filter_var($formEmail, FILTER_VALIDATE_EMAIL)) {
    $data['formEmail'] = $formEmail;
}
if ($contactInfo !== null) {
    $existing = isset($data['contactInfo']) && is_array($data['contactInfo']) ? $data['contactInfo'] : [];
    $data['contactInfo'] = array_merge($existing, $contactInfo);
}
if ($headerLogoUrl !== null) {
    $data['headerLogoUrl'] = $headerLogoUrl === '' ? '' : $headerLogoUrl;
}
if ($smtpHost !== null) $data['smtpHost'] = $smtpHost;
if ($smtpPort !== null) $data['smtpPort'] = $smtpPort;
if ($smtpUser !== null) $data['smtpUser'] = $smtpUser;
if ($smtpPass !== null && $smtpPass !== '') $data['smtpPass'] = $smtpPass;
if ($smtpSecure !== null) $data['smtpSecure'] = in_array(strtolower($smtpSecure), ['tls', 'ssl', '']) ? strtolower($smtpSecure) : 'tls';
if ($recoveryEmail !== null && ($recoveryEmail === '' || filter_var($recoveryEmail, FILTER_VALIDATE_EMAIL))) {
    $data['recoveryEmail'] = $recoveryEmail;
}
if ($secondaryRecoveryEmail !== null && ($secondaryRecoveryEmail === '' || filter_var($secondaryRecoveryEmail, FILTER_VALIDATE_EMAIL))) {
    $data['secondaryRecoveryEmail'] = $secondaryRecoveryEmail;
}
if ($recoveryAnswer1 !== null && $recoveryAnswer1 !== '') $data['recoveryAnswer1Hash'] = password_hash($recoveryAnswer1, PASSWORD_DEFAULT);
if ($recoveryAnswer2 !== null && $recoveryAnswer2 !== '') $data['recoveryAnswer2Hash'] = password_hash($recoveryAnswer2, PASSWORD_DEFAULT);
if ($recoveryAnswer3 !== null && $recoveryAnswer3 !== '') $data['recoveryAnswer3Hash'] = password_hash($recoveryAnswer3, PASSWORD_DEFAULT);

if (empty($data)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Provide formEmail, contactInfo, headerLogoUrl, and/or SMTP settings']);
    exit;
}

if (file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)) === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Could not save']);
    exit;
}

echo json_encode(['ok' => true]);
