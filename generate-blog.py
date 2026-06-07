#!/usr/bin/env python3
"""Generate 300 blog article HTML files. Run: python3 scripts/generate-blog.py"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
BLOG_DIR = os.path.join(PROJECT_DIR, 'blog')
ARTICLES_DIR = os.path.join(BLOG_DIR, 'articles')

DISCLAIMER = 'Natural stone materials vary in colour, veining, and pattern. Material performance can vary depending on installation conditions and maintenance.'

INTRO_TEMPLATES = [
    lambda t: f"Choosing the right surfaces for your home can feel overwhelming. Whether you're planning a kitchen renovation, updating a bathroom, or exploring options for new countertops, understanding your choices helps you make informed decisions. This guide covers {t.lower()} to support homeowners and builders across Ontario.",
    lambda t: f"Homeowners in the GTA and across Ontario often ask about {t.lower()}. Stone Trend has supported residential and commercial projects with stone fabrication and installation for years. Here we share practical information to help you plan your next project.",
    lambda t: f"When it comes to {t.lower()}, there's a lot to consider. From material selection to installation timing, small details can affect the outcome. This article offers guidance for homeowners and builders looking for reliable information.",
    lambda t: f"Whether you're in Toronto, Richmond Hill, Markham, or elsewhere in Ontario, {t.lower()} is a common topic for anyone upgrading their space. We've compiled helpful information based on our experience in stone fabrication and installation.",
]

SECTION_CONTENT = {
    'overview': [
        'Understanding the basics helps you communicate effectively with fabricators and designers. Many homeowners find that a bit of research before visiting showrooms leads to better outcomes. Taking time to learn about material options, typical costs, and installation processes can reduce surprises and help you ask the right questions when meeting with professionals.',
        'The first step is often understanding what options are available. Different materials offer different benefits, and what works well in one home may not suit another. Your lifestyle, cooking habits, and design preferences all play a role in selecting the right surface for your space.',
        'Material selection often depends on your lifestyle, budget, and design preferences. There is no single "best" choice—only what fits your project best. Consulting with experienced fabricators in the GTA or Ontario can help you weigh the pros and cons of each option.',
    ],
    'materials': [
        'Stone materials such as quartz, granite, quartzite, marble, and porcelain each have distinct characteristics. Quartz is an engineered product known for consistency and low maintenance; natural stones like granite and quartzite offer unique veining and colour variation that many homeowners appreciate. Porcelain slabs have become increasingly popular for their versatility and performance in a range of applications.',
        'Engineered quartz is often selected for kitchens and bathrooms due to its low maintenance requirements. Natural stone can perform well when properly maintained and sealed as recommended by your fabricator. Each material has strengths that may suit different households and usage patterns.',
        'Porcelain slabs have grown in popularity for their versatility. They can be used in applications where other materials may not be suitable, including some outdoor settings. Large-format porcelain offers design flexibility and is often chosen for modern, minimalist kitchens and bathrooms.',
    ],
    'cost': [
        'Costs vary based on material type, slab size, edge profile, and installation complexity. Getting quotes from local fabricators in the GTA or Ontario is the best way to understand pricing for your project. Be sure to ask what is included—some quotes cover fabrication and installation, while others may itemize these separately.',
        'Budget planning should include material, fabrication, and installation. Some homeowners are surprised by the range of options available at different price points. Mid-range materials can offer an attractive balance of aesthetics and performance without the premium cost of exotic stones.',
        'Regional pricing in Toronto, Richmond Hill, Markham, and the broader GTA can differ based on competition, supply, and overhead. It is worth contacting a few fabricators to compare options and understand what drives price differences in your area.',
    ],
    'maintenance': [
        'Regular cleaning with mild soap and water is often sufficient for many stone surfaces. Avoid harsh chemicals and abrasive cleaners, as these can affect the finish over time. Wiping up spills promptly, especially acidic substances, can help maintain the appearance of your countertops.',
        'Sealing requirements depend on the material. Natural stone such as granite and marble typically benefits from periodic sealing; quartz generally does not require sealing. Your fabricator can provide specific care instructions for the material you choose.',
        'Proper care can help surfaces perform well over time. Follow the care instructions provided by your fabricator for your specific material. Using cutting boards and trivets can help protect surfaces from scratches and heat exposure.',
    ],
    'installation': [
        'Professional installation is recommended for stone countertops. The process typically involves templating, fabrication, and careful installation to ensure a proper fit. Stone slabs are heavy and require experienced handlers to avoid damage during delivery and installation.',
        'Installation timelines vary. From initial measurement to final installation, many projects are completed within a few weeks, though complex projects or custom work may take longer. Discuss the timeline with your fabricator early in the process.',
        'Working with an experienced fabricator can help avoid common installation issues. Ask about their process, what to expect during the project, and how they handle cutouts for sinks and cooktops. Good communication throughout the project helps ensure a smooth experience.',
    ],
    'design': [
        'Design choices such as edge profile, thickness, and colour can significantly affect the look of your space. Consider how your countertops will pair with cabinets, backsplash, and flooring. Many homeowners bring samples or photos to showroom appointments to visualize combinations.',
        'Trends in kitchen and bathroom design evolve. What matters most is choosing something that fits your style and will work for your household for years to come. Timeless options can age well, while bold choices may suit those who enjoy updating their space more frequently.',
        'Neutral tones remain popular for their versatility and ability to work with various cabinet colours and styles. Bold veining and dramatic patterns can create a statement, while subtle options offer a more understated look. Viewing full slabs in person helps you appreciate the natural variation in stone.',
    ],
    'local': [
        'Stone Trend serves the GTA, including Toronto, Richmond Hill, Markham, and surrounding Ontario communities. Local fabricators can offer slab selection, custom fabrication, and professional installation. Working with a nearby fabricator can simplify communication and reduce lead times for your project.',
        'When sourcing materials in Ontario, consider working with fabricators who have established relationships with suppliers. This can affect availability and lead times. Fabricators with strong supplier networks may have access to a wider selection of slabs and colours.',
        'Homeowners in Richmond Hill, Markham, and the broader Toronto area have access to a range of stone options. Visiting showrooms and viewing slabs in person is often recommended, as photos can differ from the actual appearance of natural stone due to lighting and variation.',
    ],
}

CONCLUSION_TEMPLATES = [
    lambda t: f"When it comes to {t.lower()}, taking time to research and consult with experienced fabricators can lead to a result you are happy with. Stone Trend supports residential and commercial projects across Ontario with fabrication and installation services.",
    lambda t: f"We hope this guide has provided useful information about {t.lower()}. For personalized advice and quotes, reach out to a local fabricator. Stone Trend serves the GTA and Ontario with stone countertop fabrication and installation.",
    lambda t: f"Understanding {t.lower()} helps you make informed decisions for your home. Whether you are in Toronto, Richmond Hill, Markham, or elsewhere in Ontario, working with a qualified fabricator can make the process smoother.",
]

HEADINGS = [
    'Understanding the Basics', 'Material Options and Benefits', 'Cost Considerations',
    'Care and Maintenance', 'Installation Process', 'Design and Style Tips',
    'Local Options in Ontario', 'What to Look For', 'Key Considerations',
    'Practical Tips for Homeowners',
]

FAQ_PAIRS = [
    ('What should I consider when choosing countertop materials?', 'Consider your lifestyle, budget, design preferences, and maintenance expectations. Different materials suit different needs. Consulting with a fabricator can help narrow your options.'),
    ('How often do natural stone countertops need sealing?', 'Sealing frequency depends on the material and use. Granite and marble often benefit from sealing every 1–2 years, though this can vary. Your fabricator can provide specific recommendations.'),
    ('Is quartz better than granite?', 'Both have benefits. Quartz offers consistency and low maintenance; granite provides natural variation and is known for durability. The right choice depends on your preferences and project.'),
    ('How long does countertop installation take?', 'Many projects are completed within 2–4 weeks from measurement to installation. Complex projects or custom work may take longer. Your fabricator can provide a timeline.'),
    ('Can I use stone countertops in my bathroom?', 'Yes. Quartz, granite, quartzite, and other stone materials are commonly used for bathroom vanities. Proper sealing for natural stone can help in high-moisture areas.'),
    ('What is the cost of new countertops in Ontario?', 'Costs vary by material, size, and complexity. Getting quotes from local fabricators in the GTA or Ontario is the best way to understand pricing for your specific project.'),
    ('Does Stone Trend serve the Toronto area?', 'Yes. Stone Trend serves the GTA, including Toronto, Richmond Hill, Markham, and surrounding Ontario communities with stone fabrication and installation.'),
    ('What is the difference between quartz and quartzite?', 'Quartz is engineered stone; quartzite is natural stone. They look and perform differently. Quartzite tends to have more natural variation; quartz offers consistency.'),
    ('Are porcelain slabs suitable for kitchens?', 'Porcelain slabs can work well for kitchen countertops. They are often selected for their durability and resistance to heat and staining. Discuss your specific needs with a fabricator.'),
    ('How do I care for my stone countertops?', 'Regular cleaning with mild soap and water is typically sufficient. Avoid harsh chemicals. Natural stone may require periodic sealing. Follow care instructions from your fabricator.'),
    ('What countertop thickness should I choose?', '2cm and 3cm are common. 3cm is often used for edges that do not require a buildup; 2cm may need support for overhangs. Your fabricator can advise.'),
    ('Do countertops add resale value?', 'Quality countertops can be a selling point. Buyers often notice updated kitchens and bathrooms. The impact varies by market and the overall condition of the home.'),
]


def escape_html(s):
    if not s:
        return ''
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_article(title, index):
    seed = sum(ord(c) for c in title) + index
    keys = list(SECTION_CONTENT.keys())
    num_sections = 4 + (seed % 3)

    intro = INTRO_TEMPLATES[seed % len(INTRO_TEMPLATES)](title)
    conclusion = CONCLUSION_TEMPLATES[(seed + 5) % len(CONCLUSION_TEMPLATES)](title)

    sections = []
    for i in range(num_sections):
        h2 = HEADINGS[(seed + i * 13) % len(HEADINGS)]
        paragraphs = []
        for j in range(3):
            key = keys[(seed + i + j) % len(keys)]
            opts = SECTION_CONTENT[key]
            paragraphs.append(opts[(seed + i * 7 + j) % len(opts)])
        sections.append({'h2': h2, 'paragraphs': paragraphs})

    faq_count = 3 + (seed % 3)
    used = set()
    faq = []
    for i in range(faq_count + 5):
        if len(faq) >= 5:
            break
        idx = (seed + i * 11) % len(FAQ_PAIRS)
        if idx not in used:
            used.add(idx)
            faq.append(FAQ_PAIRS[idx])

    return {
        'intro': intro,
        'sections': sections,
        'conclusion': conclusion,
        'faq': faq,
    }


HEADER_HTML = '''<!DOCTYPE html>
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
          <a href="../index.html" class="btn btn-outline">&larr; Back to Blog</a>
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

</html>'''


def main():
    # Load articles from blog-data.js
    data_path = os.path.join(BLOG_DIR, 'blog-data.js')
    with open(data_path, 'r') as f:
        content = f.read()
    match = re.search(r'window\.BLOG_ARTICLES = (\[[\s\S]*?\]);', content)
    if not match:
        print('Could not parse blog-data.js')
        return
    articles = json.loads(match.group(1))

    os.makedirs(ARTICLES_DIR, exist_ok=True)

    for i, art in enumerate(articles):
        slug = art['slug']
        title = art['title']
        category = art['category']

        content_data = generate_article(title, i)

        sections_html = ''
        for s in content_data['sections']:
            paras = ''.join(f'<p>{escape_html(p)}</p>' for p in s['paragraphs'])
            sections_html += f'<section><h2>{escape_html(s["h2"])}</h2>{paras}</section>\n\n          '

        faq_html = ''
        for q, a in content_data['faq']:
            faq_html += f'<div class="faq-item"><dt>{escape_html(q)}</dt><dd>{escape_html(a)}</dd></div>\n              '

        meta_desc = f'Learn about {title.lower()}. Stone Trend offers stone fabrication and countertop installation across the GTA and Ontario.'
        if len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + '...'

        html = HEADER_HTML
        html = html.replace('{{TITLE}}', escape_html(title))
        html = html.replace('{{META_DESC}}', escape_html(meta_desc))
        html = html.replace('{{CATEGORY}}', escape_html(category))
        html = html.replace('{{INTRO}}', escape_html(content_data['intro']))
        html = html.replace('{{SECTIONS}}', sections_html.strip())
        html = html.replace('{{CONCLUSION}}', escape_html(content_data['conclusion']))
        html = html.replace('{{DISCLAIMER}}', escape_html(DISCLAIMER))
        html = html.replace('{{FAQ}}', faq_html.strip())

        out_path = os.path.join(ARTICLES_DIR, f'{slug}.html')
        with open(out_path, 'w') as f:
            f.write(html)
        print(f'Generated: {slug}.html')

    # Update blog-index.json
    index_data = {'articles': [{'slug': a['slug'], 'title': a['title'], 'category': a['category']} for a in articles]}
    with open(os.path.join(BLOG_DIR, 'blog-index.json'), 'w') as f:
        json.dump(index_data, f, indent=2)
    print(f'\nGenerated {len(articles)} articles and blog-index.json')


if __name__ == '__main__':
    main()
