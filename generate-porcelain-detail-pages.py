#!/usr/bin/env python3
"""Generate individual porcelain slab detail pages."""
import json
import html
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-porcelain.json"
PORCELAIN_DIR = Path(__file__).parent.parent / "porcelain"

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
    return html.unescape(name).replace("&nbsp;", " ").strip()


def clean_spec(val):
    if not val or str(val).strip() in ("&nbsp;", ""):
        return None
    return str(val).replace("&nbsp;", " ").strip()


def get_thickness(s):
    if s.get("format") == "tile":
        return None
    t = clean_spec(s.get("thickness"))
    return t if t else None


def get_description(s):
    raw = s.get("description")
    if raw:
        raw = raw.strip()
        # All porcelain is suitable for floors and walls; ensure it's stated
        low = raw.lower()
        if "floor" not in low and "wall" not in low:
            raw = raw.rstrip(".") + ". Suitable for floors and walls."
        return raw
    colors = s.get("colors", [])
    thickness = get_thickness(s)
    color_str = ", ".join(colors).replace("multicolour", "multi-tone")
    if len(colors) >= 2 and "multicolour" not in colors:
        color_str = color_str + " tones"
    elif len(colors) == 1:
        color_str = color_str + " porcelain"
    if s.get("format") == "tile":
        return f"{color_str.capitalize()} porcelain. Available in tile formats. Suitable for floors, walls, and feature applications."
    return f"{color_str.capitalize()} large-format porcelain. Available in {thickness or '12 mm'}. Suitable for floors, walls, countertops, and feature applications."


def get_material(slug):
    """Material per series (from Olympia site)."""
    if not slug:
        return "Porcelain"
    if slug.startswith("aequa"):
        return "Coloured-Base, Porcelain"
    if slug.startswith("antikas"):
        return "Glazed Porcelain"
    return "Porcelain, Unglazed Porcelain"


def get_tech_specs(slug):
    """Technical standards per series (exact refs from Olympia)."""
    if slug and slug.startswith("aequa"):
        return [
            ("Water Absorption", "ISO 10545-3"),
            ("Deep Abrasion Resistance", "ISO 10545-6"),
            ("Chemical Resistance", "ISO 10545-13"),
            ("Frost Resistance", "ISO 10545-12"),
            ("Dynamic C.O.F.", "ANSI A137.1:2012"),
        ]
    if slug and slug.startswith("antikas"):
        return [
            ("Water Absorption", "ASTM C-373"),
            ("Chemical Resistance", "ASTM C-650"),
            ("Dynamic C.O.F.", "ANSI A137.1:2012"),
            ("Visible Surface Abrasion Resistance", "ASTM C-1027"),
        ]
    # Quebec and default
    return [
        ("Water Absorption", "ISO 10545-3"),
        ("Bending Strength", "ISO 10545-4"),
        ("Chemical Resistance", "ISO 10545-13"),
        ("Frost Resistance", "ISO 10545-12"),
        ("Dynamic C.O.F.", "ASTM C-1028"),
        ("Slip Resistance", "DIN 51130"),
    ]


def get_dimensions(s):
    """Dimensions/sheet size per series."""
    slug = s.get("slug", "")
    if slug.startswith("antikas"):
        return "Confirm with Stone Trend for dimensions and availability."
    if s.get("colour") and slug and slug.startswith("quebec"):
        return '11.93" × 19.88" (sheet size)'
    if s.get("colour") and slug and slug.startswith("aequa"):
        return '50.5cm × 30.3cm × 0.6cm\n11.93" × 19.88" × 0.24"'
    if s.get("colour"):
        return '11.93" × 19.88" (sheet size)'
    return "Large-format slab sizes vary by series; confirm with Stone Trend for current dimensions and availability."


def render_page(s):
    name = fix_name(s.get("name", ""))
    slug = s.get("slug", "")
    img = s.get("img_large") or s.get("img_small") or ""
    if not img and slug:
        img = f"images/porcelain/{slug}.png"
    if img and not img.startswith("http"):
        img = "../" + img
    code = clean_spec(s.get("code"))
    thickness = get_thickness(s)
    colors = s.get("colors", [])
    category = s.get("category", "light").capitalize()
    desc = get_description(s)
    # Allow multi-paragraph descriptions (split on double newline)
    desc_paragraphs = [p.strip() for p in desc.split("\n\n") if p.strip()]
    desc_html = "\n            ".join(
        f'<p class="slab-detail-desc">{html.escape(p)}</p>' for p in desc_paragraphs
    ) or f'<p class="slab-detail-desc">{html.escape(desc)}</p>'

    dimensions = clean_spec(s.get("dimensions")) or get_dimensions(s)

    specs = []
    if code:
        specs.append(("Product code", code))
    if s.get("colour"):
        specs.append(("Colour", s.get("colour")))
    specs.append(("Material", get_material(slug)))
    # Quebec: sheet and stock sizes per Olympia
    if slug and slug.startswith("quebec"):
        specs.append(("Stock sizes", '1" x 1", 2" x 2"'))
        specs.append(("Sheet size", '11.93" x 19.88"'))
    # Aequa: thickness and dimensions
    if thickness:
        specs.append(("Thickness", thickness))
    if slug == "antikas" or slug.startswith("antikas_"):
        specs.append(("Shade variation", "V-2"))
        specs.append(("Edge type", "Non-rectified"))
    if not s.get("colour") and category and not (slug or "").startswith("antikas"):
        specs.append(("Category", category))
    if colors and not s.get("colour") and not (slug or "").startswith("antikas"):
        specs.append(("Colours", ", ".join(c.title() for c in colors)))
    if slug and slug.startswith("aequa") and s.get("colour"):
        specs.append(("Sheet size", '11.93" x 19.88"'))
    specs.append(("Dimensions", dimensions))

    spec_rows = "\n".join(
        f'                <tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v)).replace(chr(10), "<br>")}</td></tr>'
        for k, v in specs
    )

    # Quebec Collection note (Feldspar) – only for Quebec series
    feldspar_note = ''
    if slug and slug.startswith("quebec"):
        feldspar_note = '''
            <p class="slab-detail-note">Quebec Collection colours contain feldspar, a mineral that aids in tile maintenance by making cleaning easier. Sheet size 11.93" × 19.88".</p>'''

    # Technical standards – per series (exact refs from Olympia)
    tech_specs = get_tech_specs(slug)
    tech_rows = "\n".join(
        f'                <tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>'
        for k, v in tech_specs
    )

    return f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(name)} | Porcelain Slabs | Stone Trend</title>
  <meta name="description" content="{html.escape(name)} porcelain slab. {html.escape(desc[:120])}..." />
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
          <a href="../porcelain-slabs.html">Porcelain</a>
          <span aria-hidden="true">/</span>
          <span>{html.escape(name)}</span>
        </nav>

        <div class="slab-detail">
          <div class="slab-detail-media">
            <img src="{html.escape(img)}" alt="{html.escape(name)}" class="slab-detail-image" width="800" height="600">
          </div>
          <div class="slab-detail-info">
            <h1 class="slab-detail-title">{html.escape(name)}</h1>
{desc_html}
{feldspar_note}
            <table class="slab-specs">
              <tbody>
{spec_rows}
              </tbody>
            </table>
            <h3 class="slab-specs-heading">Technical standards</h3>
            <table class="slab-specs">
              <tbody>
{tech_rows}
              </tbody>
            </table>
            <div class="slab-detail-actions">
              <a href="../index.html#bidding" class="btn btn-cta">Request a quote</a>
            </div>
          </div>
        </div>

        <p class="small" style="margin-top: 2rem;">
          <a href="../porcelain-slabs.html">← Back to porcelain catalogue</a>
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
    if not DATA.exists():
        print(f"Data file not found: {DATA}")
        return
    with open(DATA) as f:
        slabs = json.load(f)

    PORCELAIN_DIR.mkdir(exist_ok=True)

    for s in slabs:
        slug = s.get("slug", "")
        if not slug:
            continue
        html_content = render_page(s)
        out_path = PORCELAIN_DIR / f"{slug}.html"
        with open(out_path, "w") as f:
            f.write(html_content)

    print(f"Generated {len(slabs)} porcelain detail pages in {PORCELAIN_DIR}")


if __name__ == "__main__":
    main()
