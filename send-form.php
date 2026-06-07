<?php
/**
 * Send form submissions to Stone Trend email. No mail client opens.
 * POST: form_type = quote | contact | partner, plus the form fields.
 * Optional: attachment (file) for quote form.
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
$to = 'owenkoja@stonetrend.ca';
if (file_exists($configFile)) {
    $config = json_decode(file_get_contents($configFile), true);
    if (!empty($config['formEmail'])) {
        $to = trim($config['formEmail']);
    }
}
$from = 'noreply@' . (isset($_SERVER['HTTP_HOST']) ? preg_replace('/^www\./', '', $_SERVER['HTTP_HOST']) : 'stonetrend.ca');
$formType = isset($_POST['form_type']) ? $_POST['form_type'] : '';

if ($formType === 'quote') {
    $name = trim((string) ($_POST['name'] ?? ''));
    $company = trim((string) ($_POST['company'] ?? ''));
    $email = trim((string) ($_POST['email'] ?? ''));
    $phone = trim((string) ($_POST['phone'] ?? ''));
    $projectType = trim((string) ($_POST['project-type'] ?? ''));
    $location = trim((string) ($_POST['location'] ?? ''));
    $measurements = trim((string) ($_POST['measurements'] ?? ''));
    $materialsPref = trim((string) ($_POST['materials-preference'] ?? ''));

    $subject = 'Stone Trend – Project submission' . ($name ? ' from ' . $name : '');
    $body = "Project submission from Stone Trend website\n\n";
    $body .= "Name: " . ($name ?: '—') . "\n";
    $body .= "Company: " . ($company ?: '—') . "\n";
    $body .= "Email: " . ($email ?: '—') . "\n";
    $body .= "Phone: " . ($phone ?: '—') . "\n";
    $body .= "Project type: " . ($projectType ?: '—') . "\n";
    $body .= "Project location: " . ($location ?: '—') . "\n\n";
    $body .= "Measurements & scope:\n" . ($measurements ?: '—') . "\n\n";
    $body .= "Material preferences:\n" . ($materialsPref ?: '—') . "\n\n";
    $body .= "(If the visitor had a file attachment, it is attached to this email.)\n";

    $replyTo = $email ?: $from;
} elseif ($formType === 'contact') {
    $name = trim((string) ($_POST['contact-name'] ?? ''));
    $email = trim((string) ($_POST['contact-email'] ?? ''));
    $company = trim((string) ($_POST['contact-company'] ?? ''));
    $topic = trim((string) ($_POST['contact-topic'] ?? ''));
    $message = trim((string) ($_POST['contact-message'] ?? ''));

    $subject = 'Stone Trend – Contact' . ($topic ? ' [' . $topic . ']' : '') . ($name ? ' from ' . $name : '');
    $body = "Contact form submission from Stone Trend website\n\n";
    $body .= "Name: " . ($name ?: '—') . "\n";
    $body .= "Email: " . ($email ?: '—') . "\n";
    $body .= "Company: " . ($company ?: '—') . "\n";
    $body .= "Topic: " . ($topic ?: '—') . "\n\n";
    $body .= "Message:\n" . ($message ?: '—') . "\n";

    $replyTo = $email ?: $from;
} elseif ($formType === 'partner') {
    $company = trim((string) ($_POST['partner-company'] ?? ''));
    $contactName = trim((string) ($_POST['partner-contact-name'] ?? ''));
    $email = trim((string) ($_POST['partner-email'] ?? ''));
    $phone = trim((string) ($_POST['partner-phone'] ?? ''));
    $tradeType = trim((string) ($_POST['partner-trade-type'] ?? ''));
    $serviceArea = trim((string) ($_POST['partner-service-area'] ?? ''));
    $website = trim((string) ($_POST['partner-website'] ?? ''));
    $notes = trim((string) ($_POST['partner-notes'] ?? ''));

    $subject = 'Stone Trend – Partner inquiry' . ($company ? ' from ' . $company : $contactName ? ' from ' . $contactName : '');
    $body = "Partner inquiry from Stone Trend website\n\n";
    $body .= "Company: " . ($company ?: '—') . "\n";
    $body .= "Primary contact: " . ($contactName ?: '—') . "\n";
    $body .= "Email: " . ($email ?: '—') . "\n";
    $body .= "Phone: " . ($phone ?: '—') . "\n";
    $body .= "Trade / service category: " . ($tradeType ?: '—') . "\n";
    $body .= "Service area: " . ($serviceArea ?: '—') . "\n\n";
    $body .= "Website / social links:\n" . ($website ?: '—') . "\n\n";
    $body .= "Notes about company:\n" . ($notes ?: '—') . "\n";

    $replyTo = $email ?: $from;
} else {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Unknown form type']);
    exit;
}

$boundary = '----=_Part_' . md5(uniqid());
$headers = "From: $from\r\n";
$headers .= "Reply-To: $replyTo\r\n";
$headers .= "Subject: $subject\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: multipart/mixed; boundary=\"$boundary\"\r\n";
$bodyPart = "--$boundary\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n\r\n$body\r\n";

$attachmentAdded = false;
if ($formType === 'quote' && !empty($_FILES['attachment']['tmp_name']) && is_uploaded_file($_FILES['attachment']['tmp_name'])) {
    $file = $_FILES['attachment'];
    $name = $file['name'] ?: 'attachment';
    $content = file_get_contents($file['tmp_name']);
    if ($content !== false) {
        $content = chunk_split(base64_encode($content));
        $bodyPart .= "--$boundary\r\n";
        $bodyPart .= "Content-Type: application/octet-stream; name=\"" . addslashes($name) . "\"\r\n";
        $bodyPart .= "Content-Transfer-Encoding: base64\r\n";
        $bodyPart .= "Content-Disposition: attachment; filename=\"" . addslashes($name) . "\"\r\n\r\n";
        $bodyPart .= $content . "\r\n";
        $attachmentAdded = true;
    }
}
$bodyPart .= "--$boundary--\r\n";

require_once __DIR__ . '/mail-helper.php';
$fullMessage = $headers . "\r\n" . $bodyPart;
$sent = send_site_mail($to, $subject, $fullMessage, ['from' => $from, 'replyTo' => $replyTo, 'bodyIsRaw' => true]);

if ($sent) {
    echo json_encode(['ok' => true, 'message' => 'Thank you. Your submission has been sent.']);
} else {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Could not send email. Please try again or email us directly.']);
}
