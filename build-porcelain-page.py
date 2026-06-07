#!/usr/bin/env python3
"""Build porcelain-slabs.html from porcelain JSON data."""
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "olympia-porcelain.json"
OUT = ROOT / "porcelain-slabs.html"
THUMBS = ROOT / "images" / "porcelain" / "thumbs"
IMAGES = ROOT / "images" / "porcelain"


def catalogue_image(slug, remote_img=""):
    if slug:
        for folder in (THUMBS, IMAGES):
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidate = folder / f"{slug}{ext}"
                if candidate.exists():
                    return str(candidate.relative_to(ROOT)).replace("\\", "/")
    return remote_img or (f"images/porcelain/{slug}.png" if slug else "")


def fix_name(name):
    if not name:
        return name
    s = html.unescape(name)
    return s.replace("&nbsp;", " ").strip()


def clean_spec(val):
    if not val or str(val).strip() in ("&nbsp;", ""):
        return None
    return str(val).replace("&nbsp;", " ").strip()


def get_description(s):
    if s.get("description"):
        return s.get("description")
    name = fix_name(s.get("name", ""))
    colors = s.get("colors", [])
    thickness = clean_spec(s.get("thickness")) or "12 mm"
    color_str = ", ".join(colors).replace("multicolour", "multi-tone")
    if len(colors) >= 2 and "multicolour" not in colors:
        color_str = color_str + " tones"
    elif len(colors) == 1:
        color_str = color_str + " porcelain"
    parts = [f"{color_str.capitalize()} large-format porcelain."]
    parts.append(f"Available in {thickness}.")
    parts.append("Suitable for floors, walls, countertops, and feature applications.")
    return " ".join(parts)


def get_catalogue_description(s):
    """Short teaser for the listing page. Use product description (reworded from Olympia); keep exact specs."""
    full = (s.get("description") or "").strip()
    if full and "Dot-mounted" in full:
        return (
            'Dot-mounted unglazed porcelain in speckled and solid colours in 2"×2" format. '
            'Cove Base, Pool nosing, and hexagon mosaics in select colours.'
        )
    if full and "Natural wood-look" in full:
        return 'Natural wood-look coloured-base porcelain planks with a contemporary colour palette.'
    if full and "Glazed porcelain" in full:
        return 'Glazed porcelain series with a worn stone look. Shade variation V-2, non-rectified edge.'
    if full:
        first = full.split(".")[0].strip()
        return first + "." if first else get_description(s)
    return get_description(s)


def get_thickness_filter(slab):
    if slab.get("format") == "tile":
        return ""
    t = str(slab.get("thickness", "") or "").lower().replace(" ", "")
    vals = []
    if "2cm" in t or ("2" in t and "cm" in t):
        vals.append("2cm")
    if "3cm" in t or ("3" in t and "cm" in t):
        vals.append("3cm")
    if "6mm" in t or "6" in t and "mm" in t:
        vals.append("6mm")
    if "12mm" in t or "12" in t and "mm" in t:
        vals.append("12mm")
    return " ".join(vals) if vals else ""


def main():
    if not DATA.exists():
        print(f"Data file not found: {DATA}")
        return
    with open(DATA) as f:
        slabs = json.load(f)

    # Show newest / stone-look slabs first; Quebec tiles and earlier entries last.
    slabs = list(reversed(slabs))

    if not slabs:
        print("No porcelain slabs in data. Run fetch-olympia-slabs-porcelain.py first.")
        return

    cards = []
    for i, s in enumerate(slabs):
        name = fix_name(s["name"])
        slug = s.get("slug", "")
        remote = s.get("img_large") or s.get("img_small") or ""
        img = catalogue_image(slug, remote)
        desc = get_catalogue_description(s)
        category = s.get("category", "light")
        product_type = s.get("product_type", "slabs")
        colors = s.get("colors", [])
        colors_attr = " ".join(html.escape(c) for c in colors)
        thickness_attr = get_thickness_filter(s)
        detail_url = f"porcelain/{slug}.html" if slug else ""
        cards.append(f'''          <article class="gallery-item porcelain-slab-card" data-category="{html.escape(category)}" data-product-type="{html.escape(product_type)}" data-colors="{colors_attr}" data-thickness="{html.escape(thickness_attr)}">
            <a href="{html.escape(detail_url)}" class="marble-slab-image-link" aria-label="View {html.escape(name)} details">
              <img src="{html.escape(img)}" alt="{html.escape(name)}" class="marble-slab-thumb" loading="lazy" width="400" height="400">
            </a>
            <div class="gallery-info">
              <h3><a href="{html.escape(detail_url)}" class="marble-slab-title-link">{html.escape(name)}</a></h3>
              <p>{html.escape(desc)}</p>
              <a href="{html.escape(detail_url)}" class="marble-view-details">View details <span aria-hidden="true">→</span></a>
            </div>
          </article>''')

    cards_html = "\n".join(cards)

    with open(OUT) as f:
        content = f.read()

    pattern = r'(<div class="gallery-grid" id="porcelain-gallery-grid"[^>]*>)(.*?)(</div>\s*\n\s*<p class="small")'
    def repl(m):
        return m.group(1) + "\n" + cards_html + "\n        " + m.group(3)
    new_content = re.sub(pattern, repl, content, flags=re.DOTALL)

    # Default to all slabs + tiles visible (219 products); do not pre-filter to slabs only
    new_content = new_content.replace(
        '<option value="slabs" selected>Slabs only',
        '<option value="slabs">Slabs only',
    )
    if '<option value="" selected>All types</option>' not in new_content:
        new_content = new_content.replace(
            '<option value="">All types</option>',
            '<option value="" selected>All types</option>',
            1,
        )

    new_content = re.sub(
        r"<title>Porcelain[^<]*</title>",
        "<title>Porcelain Slabs and Tiles | Stone Trend</title>",
        new_content,
        count=1,
    )
    new_content = re.sub(
        r'<p class="eyebrow">Porcelain[^<]*</p>\s*<h2>[^<]+</h2>',
        '<p class="eyebrow">Porcelain Slabs and Tiles Catalogue</p>\n          <h2>Porcelain Slabs and Tiles</h2>',
        new_content,
        count=1,
    )

    with open(OUT, "w") as f:
        f.write(new_content)

    print(f"Updated {OUT} with {len(slabs)} porcelain slabs.")


if __name__ == "__main__":
    main()
