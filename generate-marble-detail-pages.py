#!/usr/bin/env python3
"""Generate individual marble slab detail pages."""
import json
import html
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-marble.json"
MARBLE_DIR = Path(__file__).parent.parent / "marble"

NAV = '''      <nav class="main-nav">
        <ul>
          <li class="has-dropdown">
            <button>About</button>
            <div class="dropdown">
              <a href="../index.html#about">About Stone Trend</a>
              <a href="../areas-we-service.html">Areas we service</a>
              <a href="../index.html#testimonials">Testimonials</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Residential</button>
            <div class="dropdown">
              <a href="../index.html#services">Countertop Services</a>
              <a href="../index.html#materials">Materials</a>
              <a href="../gallery.html">Residential Gallery</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Commercial</button>
            <div class="dropdown">
              <a href="../index.html#commercial">Commercial Division</a>
              <a href="../index.html#bidding">Bidding &amp; Tenders</a>
              <a href="../gallery.html">Commercial Gallery</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Materials</button>
            <div class="dropdown">
              <a href="../materials.html">All Materials</a>
              <a href="../quartz-slabs.html">Quartz</a>
              <a href="../quartzite-slabs.html">Quartzite</a>
              <a href="../granite-slabs.html">Granite</a>
              <a href="../marble-slabs.html">Marble</a>
              <a href="../porcelain-slabs.html">Porcelain</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Bidding</button>
            <div class="dropdown">
              <a href="../index.html#bidding">Submit Project</a>
              <a href="../index.html#bidding">Commercial Tenders</a>
            </div>
          </li>
          <li class="has-dropdown">
            <button>Partners</button>
            <div class="dropdown">
              <a href="../trade-partners.html">Preferred Trade Partners</a>
              <a href="../why-builders-work-with-us.html">Why builders work with us</a>
              <a href="../partner-apply.html">Become a Partner</a>
            </div>
          </li>
          <li><a href="../gallery.html">Gallery</a></li>
          <li><a href="../blog/index.html">Blog</a></li>
          <li><a href="../index.html#testimonials">Testimonials</a></li>
          <li><a href="../index.html#contact">Contact</a></li>
        </ul>
      </nav>

      <div style="display:flex; align-items:center; gap:10px;">
        <a href="../pay-invoice.html" class="btn btn-outline btn-small">Pay Invoice</a>
        <a href="../index.html#bidding" class="btn btn-cta btn-small">Start a Project</a>
      </div>'''

def fix_name(name):
    if not name:
        return name
    s = html.unescape(name)
    return s.replace("&nbsp;", " ").strip()

def clean_spec(val):
    if not val or str(val).strip() in ("&nbsp;", ""):
        return None
    return str(val).replace("&nbsp;", " ").strip()

def get_thickness(s):
    if s.get("format") == "tile":
        return None
    t = clean_spec(s.get("thickness"))
    if t:
        return t
    img = s.get("img_large") or s.get("img_small") or ""
    if img and "2CM" in img.upper():
        return "2 cm"
    return "2 cm"

def get_description(s):
    colors = s.get("colors", [])
    thickness = get_thickness(s)
    color_str = ", ".join(colors).replace("multicolour", "multi-tone")
    if len(colors) >= 2 and "multicolour" not in colors:
        color_str = color_str + " tones"
    elif len(colors) == 1:
        color_str = color_str + " marble"
    if s.get("format") == "tile":
        return f"{color_str.capitalize()} with natural veining and movement. Available in tile formats. Suitable for floors, walls, backsplashes, and feature applications."
    return f"{color_str.capitalize()} with natural veining and movement. Available in {thickness}. Suitable for countertops, vanities, and feature applications."

def render_page(s):
    name = fix_name(s.get("name", ""))
    slug = s.get("slug", "")
    img = s.get("img_large") or s.get("img_small") or ""
    url = s.get("url", "")
    code = clean_spec(s.get("code"))
    thickness = get_thickness(s)
    colors = s.get("colors", [])
    category = s.get("category", "light").capitalize()
    desc = get_description(s)

    dimensions = clean_spec(s.get("dimensions"))
    if not dimensions:
        if s.get("format") == "tile":
            dimensions = "Tile sizes: various formats including 12\" × 24\", 18\" × 18\", 12\" × 12\", and more; confirm with Stone Trend for current sizes and availability."
        else:
            dimensions = "Standard slab sizes: typically 112\" × 73\" (284 × 185 cm) or 120\" × 60\" (305 × 152 cm) for 2 cm; confirm with Stone Trend for current inventory."

    specs = []
    if thickness:
        specs.append(("Thickness", thickness))
    if code:
        specs.append(("Product code", code))
    specs.append(("Category", category))
    if colors:
        specs.append(("Colours", ", ".join(c.title() for c in colors)))
    specs.append(("Dimensions", dimensions))

    spec_rows = "\n".join(
        f'                <tr><th>{k}</th><td>{html.escape(str(v))}</td></tr>'
        for k, v in specs
    )

    return f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(name)} | Marble Slabs | Stone Trend</title>
  <meta name="description" content="{html.escape(name)} marble slab. {html.escape(desc[:120])}..." />
  <link rel="stylesheet" href="../css/styles.css" />
</head>

<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="../index.html" class="brand">
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
{NAV}
    </div>
  </header>

  <main>
    <section class="section section-light">
      <div class="container">
        <nav class="slab-breadcrumb" aria-label="Breadcrumb">
          <a href="../marble-slabs.html">Marble</a>
          <span aria-hidden="true">/</span>
          <span>{html.escape(name)}</span>
        </nav>

        <div class="slab-detail">
          <div class="slab-detail-media">
            <img src="{html.escape(img)}" alt="{html.escape(name)}" class="slab-detail-image" width="800" height="600">
          </div>
          <div class="slab-detail-info">
            <h1 class="slab-detail-title">{html.escape(name)}</h1>
            <p class="slab-detail-desc">{html.escape(desc)}</p>
            <table class="slab-specs">
              <tbody>
{spec_rows}
              </tbody>
            </table>
            <div class="slab-detail-actions">
              <a href="../index.html#bidding" class="btn btn-cta">Request a quote</a>
            </div>
          </div>
        </div>

        <p class="small" style="margin-top: 2rem;">
          <a href="../marble-slabs.html">← Back to marble catalogue</a>
        </p>
      </div>
    </section>
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
        <a href="../index.html">Back to home</a>
        <a href="../index.html#bidding">Start a project</a>
        <a href="../index.html#contact">Contact</a>
        <a href="../privacy-policy.html">Privacy policy</a>
        <a href="../terms-and-conditions.html">Terms &amp; conditions</a>
      </div>
    </div>
  </footer>

  <script src="../js/main.js"></script>
</body>

</html>'''

def main():
    with open(DATA) as f:
        slabs = json.load(f)

    MARBLE_DIR.mkdir(exist_ok=True)

    for s in slabs:
        slug = s.get("slug", "")
        if not slug:
            continue
        html_content = render_page(s)
        out_path = MARBLE_DIR / f"{slug}.html"
        with open(out_path, "w") as f:
            f.write(html_content)

    print(f"Generated {len(slabs)} marble detail pages in {MARBLE_DIR}")

if __name__ == "__main__":
    main()
