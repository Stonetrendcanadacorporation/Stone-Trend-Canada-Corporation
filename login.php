<?php
/**
 * Admin login: verify password. Tracks failed attempts by IP. After 3 failures returns needRecovery + recoveryEmail.
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

$password = isset($_POST['password']) ? (string) $_POST['password'] : '';
if ($password === '') {
    echo json_encode(['ok' => false, 'error' => 'Password required']);
    exit;
}

$ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
$attemptsFile = __DIR__ . '/data/login-attempts.json';
$configFile = __DIR__ . '/data/site-config.json';
$adminFile = __DIR__ . '/data/admin.json';
$defaultPassword = 'stonetrend';

function get_attempts($file) {
    if (!file_exists($file)) return [];
    $d = json_decode(file_get_contents($file), true);
    return is_array($d) ? $d : [];
}
function set_attempts($file, $data) {
    $dir = dirname($file);
    if (!is_dir($dir)) mkdir($dir, 0755, true);
    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT));
}
function clear_attempts_for_ip($file, $ip) {
    $data = get_attempts($file);
    if ($ip !== '' && isset($data[$ip])) {
        unset($data[$ip]);
        set_attempts($file, $data);
    }
}

$attempts = get_attempts($attemptsFile);
$now = time();
if ($ip !== '') {
    if (!isset($attempts[$ip])) $attempts[$ip] = ['count' => 0, 'at' => $now];
    $attempts[$ip]['at'] = $now;
}

if (file_exists($adminFile)) {
    $data = json_decode(file_get_contents($adminFile), true);
    $hash = isset($data['adminPasswordHash']) ? $data['adminPasswordHash'] : '';
    if ($hash !== '' && password_verify($password, $hash)) {
        if ($ip !== '') clear_attempts_for_ip($attemptsFile, $ip);
        echo json_encode(['ok' => true]);
        exit;
    }
} elseif ($password === $defaultPassword) {
    if ($ip !== '') clear_attempts_for_ip($attemptsFile, $ip);
    echo json_encode(['ok' => true]);
    exit;
}

if ($ip !== '') {
    $attempts[$ip]['count'] = isset($attempts[$ip]['count']) ? (int) $attempts[$ip]['count'] + 1 : 1;
    set_attempts($attemptsFile, $attempts);
    $count = (int) $attempts[$ip]['count'];
    $recoveryEmail = '';
    $secondaryRecoveryEmail = '';
    if (file_exists($configFile)) {
        $config = json_decode(file_get_contents($configFile), true);
        if (!empty($config['recoveryEmail'])) $recoveryEmail = trim($config['recoveryEmail']);
        if (!empty($config['secondaryRecoveryEmail'])) $secondaryRecoveryEmail = trim($config['secondaryRecoveryEmail']);
    }
    if ($count >= 3 && $recoveryEmail !== '') {
        $out = ['ok' => false, 'needRecovery' => true, 'recoveryEmail' => $recoveryEmail];
        if ($secondaryRecoveryEmail !== '') $out['secondaryRecoveryEmail'] = $secondaryRecoveryEmail;
        echo json_encode($out);
        exit;
    }
}

echo json_encode(['ok' => false, 'error' => 'Incorrect password']);
