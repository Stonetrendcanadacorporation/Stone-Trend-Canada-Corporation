<?php
/**
 * Send email via SMTP (if configured in site-config) or PHP mail().
 * Use this for form submissions and password reset so emails work on hosts where mail() is blocked.
 *
 * Config in data/site-config.json:
 *   smtpHost    - e.g. smtp.gmail.com, mail.example.com
 *   smtpPort    - 587 (TLS), 465 (SSL), or 25
 *   smtpUser    - SMTP username
 *   smtpPass    - SMTP password (or app password for Gmail)
 *   smtpSecure  - 'tls' or 'ssl' or '' for none
 *
 * If any of these are missing/empty, falls back to mail().
 */

function get_mail_config() {
    $file = __DIR__ . '/data/site-config.json';
    if (!file_exists($file)) return [];
    $data = json_decode(file_get_contents($file), true);
    return is_array($data) ? $data : [];
}

/**
 * Send an email. Returns true on success, false on failure.
 *
 * @param string $to       Recipient email
 * @param string $subject  Subject
 * @param string $body    Plain-text body (or full MIME if you set $bodyIsRaw = true)
 * @param array  $options  Optional: from, replyTo, bodyIsRaw (multipart), bodyIsHtml (HTML body)
 */
function send_site_mail($to, $subject, $body, $options = []) {
    $config = get_mail_config();
    $host = isset($config['smtpHost']) ? trim((string) $config['smtpHost']) : '';
    $port = isset($config['smtpPort']) ? (int) $config['smtpPort'] : 587;
    $user = isset($config['smtpUser']) ? trim((string) $config['smtpUser']) : '';
    $pass = isset($config['smtpPass']) ? (string) $config['smtpPass'] : '';
    $secure = isset($config['smtpSecure']) ? strtolower(trim((string) $config['smtpSecure'])) : 'tls';

    $from = isset($options['from']) ? $options['from'] : null;
    $replyTo = isset($options['replyTo']) ? $options['replyTo'] : null;
    $bodyIsRaw = !empty($options['bodyIsRaw']);
    $bodyIsHtml = !empty($options['bodyIsHtml']);

    $defaultFrom = 'noreply@' . (isset($_SERVER['HTTP_HOST']) ? preg_replace('/^www\./', '', $_SERVER['HTTP_HOST']) : 'localhost');
    if (empty($from)) $from = $defaultFrom;
    if (empty($replyTo)) $replyTo = $from;

    if ($host !== '' && $user !== '' && $pass !== '') {
        return send_via_smtp($host, $port, $secure, $user, $pass, $from, $to, $replyTo, $subject, $body, $bodyIsRaw, $bodyIsHtml);
    }

    return send_via_mail($to, $subject, $body, $from, $replyTo, $bodyIsRaw, $bodyIsHtml);
}

function send_via_mail($to, $subject, $body, $from, $replyTo, $bodyIsRaw, $bodyIsHtml = false) {
    $headers = "From: $from\r\nReply-To: $replyTo\r\n";
    if (!$bodyIsRaw) {
        $headers .= $bodyIsHtml ? "Content-Type: text/html; charset=UTF-8\r\n" : "Content-Type: text/plain; charset=UTF-8\r\n";
    }
    return @mail($to, $subject, $body, $headers);
}

function send_via_smtp($host, $port, $secure, $user, $pass, $from, $to, $replyTo, $subject, $body, $bodyIsRaw, $bodyIsHtml = false) {
    $useTls = ($secure === 'tls');
    $useSsl = ($secure === 'ssl');
    $target = ($useSsl ? 'ssl://' : '') . $host . ':' . $port;

    $errno = 0;
    $errstr = '';
    $ctx = null;
    if ($useSsl || $useTls) {
        $ctx = stream_context_create(['ssl' => ['verify_peer' => false, 'verify_peer_name' => false]]);
    }
    $sock = @stream_socket_client($target, $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx);
    if (!$sock) return false;

    $getLine = function () use ($sock) {
        $line = @fgets($sock, 512);
        return $line !== false ? trim($line) : '';
    };
    $send = function ($msg) use ($sock) {
        @fwrite($sock, $msg . "\r\n");
    };

    $getLine();
    $send("EHLO " . ($_SERVER['SERVER_NAME'] ?? 'localhost'));
    while ($line = $getLine()) {
        if (substr($line, 0, 4) === '250 ' || $line === '250') break;
    }

    if ($useTls && function_exists('stream_socket_enable_crypto')) {
        $send("STARTTLS");
        $getLine();
        if (!@stream_socket_enable_crypto($sock, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) return false;
        $send("EHLO " . ($_SERVER['SERVER_NAME'] ?? 'localhost'));
        while ($line = $getLine()) {
            if (substr($line, 0, 4) === '250 ' || $line === '250') break;
        }
    }

    $send("AUTH LOGIN");
    $getLine();
    $send(base64_encode($user));
    $getLine();
    $send(base64_encode($pass));
    $auth = $getLine();
    if (substr($auth, 0, 3) !== '235') {
        fclose($sock);
        return false;
    }

    $send("MAIL FROM:<" . extract_email($from) . ">");
    $getLine();
    $send("RCPT TO:<" . extract_email($to) . ">");
    $getLine();
    $send("DATA");
    $getLine();

    $headers = "From: $from\r\nReply-To: $replyTo\r\n";
    if (!$bodyIsRaw) {
        $headers .= $bodyIsHtml ? "Content-Type: text/html; charset=UTF-8\r\n" : "Content-Type: text/plain; charset=UTF-8\r\n";
    }
    $headers .= "Subject: $subject\r\n";
    $data = $headers . "\r\n" . $body;
    $lines = preg_split('/\r\n|\n|\r/', $data);
    foreach ($lines as $line) {
        if (strpos($line, '.') === 0) $line = '.' . $line;
        @fwrite($sock, $line . "\r\n");
    }
    @fwrite($sock, ".\r\n");
    $last = $getLine();
    $send("QUIT");
    fclose($sock);
    return substr($last, 0, 3) === '250';
}

function extract_email($addr) {
    if (preg_match('/<([^>]+)>/', $addr, $m)) return trim($m[1]);
    return trim($addr);
}
