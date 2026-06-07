<?php
/**
 * Send a test email to the configured form email address. Used to verify SMTP/mail works.
 * POST (no body required). Returns { "ok": true } or { "ok": false, "error": "..." }.
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

$configFile = __DIR__ . '/data/site-config.json';
$to = '';
if (file_exists($configFile)) {
    $config = json_decode(file_get_contents($configFile), true);
    if (!empty($config['formEmail'])) $to = trim($config['formEmail']);
}
if ($to === '' || !filter_var($to, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['ok' => false, 'error' => 'Set the form email in Settings first.']);
    exit;
}

require_once __DIR__ . '/mail-templates.php';
require_once __DIR__ . '/mail-helper.php';
$subject = 'You’re all set – Stone Trend';
$body = premium_email_message_only(
    "Your email is connected",
    "This is a quick test from your Stone Trend site. If you’re reading this, your settings are working and you’ll receive form submissions, password reset links, and account recovery emails at this address.",
    "Sent at " . date('F j, Y \a\t g:i A') . "."
);

$from = 'noreply@' . (isset($_SERVER['HTTP_HOST']) ? preg_replace('/^www\./', '', $_SERVER['HTTP_HOST']) : 'stonetrend.ca');
$sent = send_site_mail($to, $subject, $body, ['from' => $from, 'replyTo' => $from, 'bodyIsHtml' => true]);

if ($sent) {
    echo json_encode(['ok' => true, 'message' => 'Test email sent to ' . $to . '. Check your inbox (and spam folder).']);
} else {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Could not send. Add SMTP settings in Settings (e.g. GoDaddy or Gmail) and try again.']);
}
