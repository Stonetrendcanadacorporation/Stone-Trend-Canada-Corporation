<?php
/**
 * Return site config (e.g. form email). GET only.
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$file = __DIR__ . '/data/site-config.json';
$default = ['formEmail' => 'owenkoja@stonetrend.ca'];

if (file_exists($file)) {
    $data = json_decode(file_get_contents($file), true);
    if (is_array($data)) {
        unset($data['recoveryAnswer1Hash'], $data['recoveryAnswer2Hash'], $data['recoveryAnswer3Hash']);
        echo json_encode(array_merge($default, $data));
        exit;
    }
}

echo json_encode($default);
