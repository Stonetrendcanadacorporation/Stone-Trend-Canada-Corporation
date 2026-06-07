<?php
/**
 * Premium HTML email templates for Stone Trend – clean, reassuring, high-end.
 * All styles inline for email client compatibility.
 */

/**
 * Build a "Request from: IP (Location)" line for security emails.
 * Uses ip-api.com (no key required). Returns empty string on failure or private IP.
 */
function get_request_location_line($ip) {
    $ip = trim((string) $ip);
    if ($ip === '') return '';
    if (preg_match('/^(127\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|::1)/', $ip)) {
        return 'Request from: ' . $ip . ' (private network)';
    }
    $url = 'http://ip-api.com/json/' . rawurlencode($ip) . '?fields=status,city,regionName,country&lang=en';
    $ctx = stream_context_create(['http' => ['timeout' => 2]]);
    $json = @file_get_contents($url, false, $ctx);
    if ($json === false) return 'Request from: ' . $ip;
    $data = @json_decode($json, true);
    if (!is_array($data) || empty($data['status']) || $data['status'] !== 'success') {
        return 'Request from: ' . $ip;
    }
    $parts = array_filter([$data['city'] ?? '', $data['regionName'] ?? '', $data['country'] ?? '']);
    $location = implode(', ', $parts);
    return $location !== '' ? 'Request from: ' . $ip . ' (' . $location . ')' : 'Request from: ' . $ip;
}

/**
 * @param string $heading     Main heading (e.g. "You're all set")
 * @param string $intro       Short intro paragraph
 * @param string $ctaUrl      Full URL for the button
 * @param string $ctaLabel    Button text (e.g. "Reset my password")
 * @param string $footer      Optional footer line (e.g. "This link expires in 1 hour.")
 * @param string $subtext     Optional line under button (e.g. "If you didn't request this, you can ignore this email.")
 * @param string $requestFrom Optional line e.g. "Request from: 1.2.3.4 (Toronto, ON, Canada)"
 */
function premium_email_html($heading, $intro, $ctaUrl, $ctaLabel, $footer = '', $subtext = '', $requestFrom = '') {
    $ctaUrl = htmlspecialchars($ctaUrl, ENT_QUOTES, 'UTF-8');
    $heading = htmlspecialchars($heading, ENT_QUOTES, 'UTF-8');
    $intro = nl2br(htmlspecialchars($intro, ENT_QUOTES, 'UTF-8'));
    $ctaLabel = htmlspecialchars($ctaLabel, ENT_QUOTES, 'UTF-8');
    $footer = $footer !== '' ? htmlspecialchars($footer, ENT_QUOTES, 'UTF-8') : '';
    $subtext = $subtext !== '' ? nl2br(htmlspecialchars($subtext, ENT_QUOTES, 'UTF-8')) : '';
    $requestFrom = $requestFrom !== '' ? htmlspecialchars($requestFrom, ENT_QUOTES, 'UTF-8') : '';

    return '<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stone Trend</title>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #2c2c2c;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f5f5f5;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 480px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.06);">
          <tr>
            <td style="padding: 48px 40px 40px;">
              <p style="margin: 0 0 8px; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: #888;">Stone Trend</p>
              <h1 style="margin: 0 0 24px; font-size: 24px; font-weight: 600; color: #1a1a1a; letter-spacing: -0.02em;">' . $heading . '</h1>
              <p style="margin: 0 0 32px; font-size: 16px; line-height: 1.65; color: #4a4a4a;">' . $intro . '</p>
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="border-radius: 8px; background-color: #c6a75e;">
                    <a href="' . $ctaUrl . '" target="_blank" style="display: inline-block; padding: 14px 28px; font-size: 15px; font-weight: 600; color: #1a1a1a; text-decoration: none; letter-spacing: 0.02em;">' . $ctaLabel . '</a>
                  </td>
                </tr>
              </table>
              ' . ($footer !== '' ? '<p style="margin: 24px 0 0; font-size: 13px; color: #888;">' . $footer . '</p>' : '') . '
              ' . ($subtext !== '' ? '<p style="margin: 20px 0 0; font-size: 13px; line-height: 1.5; color: #888;">' . $subtext . '</p>' : '') . '
              ' . ($requestFrom !== '' ? '<p style="margin: 24px 0 0; padding-top: 16px; border-top: 1px solid #eee; font-size: 12px; color: #999;">' . $requestFrom . '</p>' : '') . '
            </td>
          </tr>
        </table>
        <p style="margin: 24px 0 0; font-size: 12px; color: #aaa;">Stone Trend Canada Corporation</p>
      </td>
    </tr>
  </table>
</body>
</html>';
}

/**
 * Simple premium email with no button – for test or notification.
 */
function premium_email_message_only($heading, $intro, $footer = '') {
    $heading = htmlspecialchars($heading, ENT_QUOTES, 'UTF-8');
    $intro = nl2br(htmlspecialchars($intro, ENT_QUOTES, 'UTF-8'));
    $footer = $footer !== '' ? htmlspecialchars($footer, ENT_QUOTES, 'UTF-8') : '';

    return '<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stone Trend</title>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #2c2c2c;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f5f5f5;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 480px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.06);">
          <tr>
            <td style="padding: 48px 40px 40px;">
              <p style="margin: 0 0 8px; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: #888;">Stone Trend</p>
              <h1 style="margin: 0 0 24px; font-size: 24px; font-weight: 600; color: #1a1a1a; letter-spacing: -0.02em;">' . $heading . '</h1>
              <p style="margin: 0; font-size: 16px; line-height: 1.65; color: #4a4a4a;">' . $intro . '</p>
              ' . ($footer !== '' ? '<p style="margin: 24px 0 0; font-size: 13px; color: #888;">' . $footer . '</p>' : '') . '
            </td>
          </tr>
        </table>
        <p style="margin: 24px 0 0; font-size: 12px; color: #aaa;">Stone Trend Canada Corporation</p>
      </td>
    </tr>
  </table>
</body>
</html>';
}
