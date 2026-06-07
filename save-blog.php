<?php
/**
 * Save blog index: add, rename (update), or delete an article.
 * POST: action=add|rename|delete, slug, title, category (for add/rename).
 * Writes blog/blog-index.json. For add, creates blog/articles/{slug}.html from stub.
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

$base = __DIR__;
$indexFile = $base . '/blog/blog-index.json';
$articlesDir = $base . '/blog/articles';

$action = isset($_POST['action']) ? trim($_POST['action']) : '';
$slug = isset($_POST['slug']) ? trim(preg_replace('/[^a-z0-9\-]/', '', strtolower($_POST['slug']))) : '';
$title = isset($_POST['title']) ? trim($_POST['title']) : '';
$category = isset($_POST['category']) ? trim($_POST['category']) : '';

if (!in_array($action, ['add', 'rename', 'delete'], true)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Invalid action']);
    exit;
}

$data = ['articles' => []];
if (file_exists($indexFile)) {
    $data = json_decode(file_get_contents($indexFile), true) ?: $data;
}
if (!isset($data['articles']) || !is_array($data['articles'])) {
    $data['articles'] = [];
}

if ($action === 'delete') {
    if ($slug === '') {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Slug required']);
        exit;
    }
    $data['articles'] = array_values(array_filter($data['articles'], function ($a) use ($slug) {
        return ($a['slug'] ?? '') !== $slug;
    }));
    $articleFile = $articlesDir . '/' . $slug . '.html';
    if (file_exists($articleFile)) {
        @unlink($articleFile);
    }
} elseif ($action === 'rename') {
    if ($slug === '' || $title === '') {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Slug and title required']);
        exit;
    }
    foreach ($data['articles'] as &$a) {
        if (($a['slug'] ?? '') === $slug) {
            $a['title'] = $title;
            if ($category !== '') $a['category'] = $category;
            break;
        }
    }
} elseif ($action === 'add') {
    if ($title === '') {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Title required']);
        exit;
    }
    if ($slug === '') {
        $slug = strtolower(preg_replace('/[^a-z0-9\-]+/', '-', trim($title)));
        $slug = trim($slug, '-');
    }
    $data['articles'][] = ['slug' => $slug, 'title' => $title, 'category' => $category ?: 'Countertops'];
    if (!is_dir($articlesDir)) {
        mkdir($articlesDir, 0755, true);
    }
    $articleFile = $articlesDir . '/' . $slug . '.html';
    if (!file_exists($articleFile)) {
        $stub = '<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>' . htmlspecialchars($title) . ' | Stone Trend Blog</title>
  <link rel="stylesheet" href="../../css/styles.css" />
  <link rel="stylesheet" href="../../css/admin-editor.css" />
</head>
<body>
  <header class="site-header"><div class="container header-inner"><a href="../../index.html" class="brand">Stone Trend</a></div></header>
  <main>
    <article class="section section-light blog-article">
      <div class="container container--narrow">
        <nav class="blog-breadcrumb"><a href="../index.html">Blog</a> / <span>' . htmlspecialchars($category ?: 'Countertops') . '</span> / <span>' . htmlspecialchars($title) . '</span></nav>
        <header class="blog-article-header">
          <p class="eyebrow">' . htmlspecialchars($category ?: 'Countertops') . '</p>
          <h1>' . htmlspecialchars($title) . '</h1>
        </header>
        <div class="blog-article-content">
          <p class="blog-intro">Edit this article in edit mode. Add your content here.</p>
        </div>
        <footer class="blog-article-footer"><a href="../index.html" class="btn btn-outline">&larr; Back to Blog</a></footer>
      </div>
    </article>
  </main>
  <footer class="site-footer"><div class="container footer-inner"><p>&copy; ' . date('Y') . ' Stone Trend</p></div></footer>
  <script src="../../js/admin-visual-editor.js"></script>
  <script src="../../js/main.js"></script>
</body>
</html>';
        file_put_contents($articleFile, $stub);
    }
}

if (!is_dir(dirname($indexFile))) {
    mkdir(dirname($indexFile), 0755, true);
}
if (file_put_contents($indexFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)) === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Could not save index']);
    exit;
}

echo json_encode(['ok' => true, 'slug' => $slug]);
