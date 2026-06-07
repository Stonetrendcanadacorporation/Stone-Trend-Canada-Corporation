#!/usr/bin/env node
/**
 * Generates 300 static HTML blog articles for Stone Trend.
 * Run: node scripts/generate-blog.js
 */

const fs = require('fs');
const path = require('path');
const { BLOG_TITLES } = require('../blog/blog-titles.js');
const { generateArticle } = require('./generate-blog-content.js');

const BLOG_DIR = path.join(__dirname, '..', 'blog');
const ARTICLES_DIR = path.join(BLOG_DIR, 'articles');

const HEADER_HTML = `<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{TITLE}} | Stone Trend Blog</title>
  <meta name="description" content="{{META_DESC}}" />
  <link rel="stylesheet" href="../../css/styles.css" />
</head>

<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="../../index.html" class="brand">
        <svg class="logo-svg logo-svg--nav" viewBox="0 0 160 160" aria-hidden="true" focusable="false">
          <g class="logo-lines">
            <path class="logo-path"
              d="M22 118 V68 L56 86 V118 Z M56 118 V58 L90 72 V118 Z M90 118 V46 L138 78 V118 Z M56 86 L106 62" />
          </g>
        </svg>
      </a>

      <button class="nav-toggle" aria-label="Toggle navigation">
        <span></span>
        <span></span>
      </button>

      <nav class="main-nav">
        <ul>
          <li class="has-dropdown">
            <button>About</button>
            <div class="dropdown">
              <a href="../../index.html#about">About Stone Trend</a>
              <a href="../../areas-we-service.html">Areas we service</a>
              <a href="../../index.html#testimonials">Testimonials</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Residential</button>
            <div class="dropdown">
              <a href="../../index.html#services">Countertop Services</a>
              <a href="../../index.html#materials">Materials</a>
              <a href="../../gallery.html">Residential Gallery</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Commercial</button>
            <div class="dropdown">
              <a href="../../index.html#commercial">Commercial Division</a>
              <a href="../../index.html#bidding">Bidding &amp; Tenders</a>
              <a href="../../gallery.html">Commercial Gallery</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Materials</button>
            <div class="dropdown">
              <a href="../../materials.html">All Materials</a>
              <a href="../../quartz-slabs.html">Quartz</a>
              <a href="../../quartzite-slabs.html">Quartzite</a>
              <a href="../../granite-slabs.html">Granite</a>
              <a href="../../marble-slabs.html">Marble</a>
              <a href="../../porcelain-slabs.html">Porcelain</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Partners</button>
            <div class="dropdown">
              <a href="../../trade-partners.html">Preferred Trade Partners</a>
              <a href="../../why-builders-work-with-us.html">Why builders work with us</a>
              <a href="../../partner-apply.html">Become a Partner</a>
            </div>
          </li>
          <li><a href="../../gallery.html">Gallery</a></li>
          <li><a href="../index.html">Blog</a></li>
          <li><a href="../../index.html#contact">Contact</a></li>
        </ul>
      </nav>

      <div style="display:flex; align-items:center; gap:10px;">
        <a href="../../pay-invoice.html" class="btn btn-outline btn-small">Pay Invoice</a>
        <a href="../../index.html#bidding" class="btn btn-cta btn-small">Start a Project</a>
      </div>
    </div>
  </header>

  <main>
    <article class="section section-light blog-article">
      <div class="container container--narrow">
        <nav class="blog-breadcrumb" aria-label="Breadcrumb">
          <a href="../index.html">Blog</a>
          <span aria-hidden="true"> / </span>
          <span>{{CATEGORY}}</span>
          <span aria-hidden="true"> / </span>
          <span>{{TITLE}}</span>
        </nav>

        <header class="blog-article-header">
          <p class="eyebrow">{{CATEGORY}}</p>
          <h1>{{TITLE}}</h1>
        </header>

        <div class="blog-article-content">
          <p class="blog-intro">{{INTRO}}</p>

          {{SECTIONS}}

          <p class="blog-conclusion">{{CONCLUSION}}</p>

          <p class="blog-disclaimer small">{{DISCLAIMER}}</p>

          <section class="blog-faq" aria-labelledby="faq-heading">
            <h2 id="faq-heading">Frequently Asked Questions</h2>
            <dl class="faq-list">
              {{FAQ}}
            </dl>
          </section>
        </div>

        <footer class="blog-article-footer">
          <a href="../index.html" class="btn btn-outline">← Back to Blog</a>
        </footer>
      </div>
    </article>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <p class="footer-brand">Stone Trend</p>
        <p class="footer-legal">
          &copy; <span id="year"></span> Stone Trend Canada Corporation. All rights reserved.
        </p>
      </div>
      <div class="footer-links">
        <a href="../../index.html">Back to home</a>
        <a href="../../index.html#bidding">Start a project</a>
        <a href="../../index.html#contact">Contact</a>
        <a href="../../privacy-policy.html">Privacy policy</a>
        <a href="../../terms-and-conditions.html">Terms &amp; conditions</a>
      </div>
    </div>
  </footer>

  <script src="../../js/main.js"></script>
</body>

</html>`;

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function generateMetaDesc(title, category) {
  const base = `Learn about ${title.toLowerCase()}. Stone Trend offers stone fabrication and countertop installation across the GTA and Ontario.`;
  return base.length > 160 ? base.substring(0, 157) + '...' : base;
}

function buildArticleHtml(article) {
  let html = HEADER_HTML;

  const sectionsHtml = article.sections
    .map(
      (s) =>
        `<section>
            <h2>${escapeHtml(s.h2)}</h2>
            ${s.paragraphs.map((p) => `<p>${escapeHtml(p)}</p>`).join('\n            ')}
          </section>`
    )
    .join('\n\n          ');

  const faqHtml = article.faq
    .map(
      ([q, a]) =>
        `<div class="faq-item">
              <dt>${escapeHtml(q)}</dt>
              <dd>${escapeHtml(a)}</dd>
            </div>`
    )
    .join('\n              ');

  html = html.replace('{{TITLE}}', escapeHtml(article.title));
  html = html.replace('{{META_DESC}}', escapeHtml(generateMetaDesc(article.title, article.category)));
  html = html.replace('{{CATEGORY}}', escapeHtml(article.category));
  html = html.replace('{{INTRO}}', escapeHtml(article.intro));
  html = html.replace('{{SECTIONS}}', sectionsHtml);
  html = html.replace('{{CONCLUSION}}', escapeHtml(article.conclusion));
  html = html.replace('{{DISCLAIMER}}', escapeHtml(article.disclaimer));
  html = html.replace('{{FAQ}}', faqHtml);

  return html;
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function main() {
  ensureDir(ARTICLES_DIR);

  const articles = [];
  for (let i = 0; i < BLOG_TITLES.length; i++) {
    const title = BLOG_TITLES[i];
    const article = generateArticle(title, i);
    articles.push(article);

    const html = buildArticleHtml(article);
    const filePath = path.join(ARTICLES_DIR, `${article.slug}.html`);
    fs.writeFileSync(filePath, html, 'utf8');
    console.log(`Generated: ${article.slug}.html`);
  }

  const indexData = {
    articles: articles.map((a) => ({
      slug: a.slug,
      title: a.title,
      category: a.category,
    })),
  };
  fs.writeFileSync(
    path.join(BLOG_DIR, 'blog-index.json'),
    JSON.stringify(indexData, null, 2),
    'utf8'
  );
  console.log('\nGenerated blog-index.json for blog listing.');
  console.log(`Total: ${articles.length} articles`);
}

main();
