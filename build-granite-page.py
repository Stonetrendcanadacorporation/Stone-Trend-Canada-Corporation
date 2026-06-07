#!/usr/bin/env python3
"""Build granite-slabs.html from granite JSON data."""
import json
import html
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-granite.json"
OUT = Path(__file__).parent.parent / "granite-slabs.html"


def fix_name(name):
    if not name:
        return name
    s = html.unescape(name)
    return s.replace("&nbsp;", " ").strip()


def clean_spec(val):
    if not val or (isinstance(val, str) and val.strip() in ("&nbsp;", "")):
        return None
    return str(val).replace("&nbsp;", " ").strip()


def get_description(s):
    name = fix_name(s.get("name", ""))
    colors = s.get("colors", [])
    is_tile = s.get("format") == "tile"
    color_str = ", ".join(colors).replace("multicolour", "multi-tone")
    if len(colors) >= 2 and "multicolour" not in colors:
        color_str = color_str + " tones"
    elif len(colors) == 1:
        color_str = color_str + " granite"
    if is_tile:
        return f"{color_str.capitalize()} with natural grain and movement. Available in tile formats. Suitable for floors, walls, backsplashes, and feature applications."
    thickness = clean_spec(s.get("thickness")) or "2 cm"
    parts = [f"{color_str.capitalize()} with natural grain and movement."]
    parts.append(f"Available in {thickness}.")
    parts.append("Suitable for countertops, vanities, and feature applications.")
    return " ".join(parts)


def get_thickness_filter(slab):
    if slab.get("format") == "tile":
        return ""
    t = str(slab.get("thickness", "") or "").lower().replace(" ", "")
    vals = []
    if "2cm" in t or ("2" in t and "cm" in t):
        vals.append("2cm")
    if "3cm" in t or ("3" in t and "cm" in t):
        vals.append("3cm")
    return " ".join(vals) if vals else "2cm"


def get_thickness_label(slab):
    """Human-readable thickness for display on card (2 cm, 3 cm, 2 cm & 3 cm, or Tile)."""
    if slab.get("format") == "tile":
        return "Tile"
    raw = clean_spec(slab.get("thickness")) or "2 cm"
    raw_lower = raw.lower().replace(" ", "")
    if "2" in raw_lower and "3" in raw_lower:
        return "2 cm & 3 cm"
    if "3" in raw_lower and "cm" in raw_lower:
        return "3 cm"
    return "2 cm"


# First 2 rows (8 cards): most aesthetic / iconic slabs
FEATURED_FIRST = [
    "bianco_antico", "black_galaxy", "blue_pearl", "black_pearl",
    "grg_sardo", "taj_mah_lf", "white_torr", "verde_bah",
]


def main():
    with open(DATA) as f:
        slabs = json.load(f)

    # Reorder: featured first (in FEATURED_FIRST order), then rest
    featured = {s.get("slug"): s for s in slabs if s.get("slug") in FEATURED_FIRST}
    ordered = []
    for slug in FEATURED_FIRST:
        if slug in featured:
            ordered.append(featured[slug])
    for s in slabs:
        if s.get("slug") not in FEATURED_FIRST:
            ordered.append(s)
    slabs = ordered

    cards = []
    for i, s in enumerate(slabs):
        name = fix_name(s["name"])
        img = s.get("img_large") or s.get("img_small") or ""
        desc = get_description(s)
        delay = (i % 3) * 60
        category = s.get("category", "light")
        colors = s.get("colors", [])
        colors_attr = " ".join(html.escape(c) for c in colors)
        thickness_attr = get_thickness_filter(s)
        thickness_label = get_thickness_label(s)
        fmt = s.get("format") or "slab"
        slug = s.get("slug", "")
        detail_url = f"granite/{slug}.html" if slug else ""
        cards.append(
            f'          <article class="gallery-item granite-slab-card" data-animate="fade-up" data-animate-delay="{delay}" '
            f'data-category="{html.escape(category)}" data-colors="{colors_attr}" data-thickness="{html.escape(thickness_attr)}" data-format="{html.escape(fmt)}">\n'
            f'            <a href="{html.escape(detail_url)}" class="granite-slab-image-link" aria-label="View {html.escape(name)} details">\n'
            f'              <img src="{html.escape(img)}" alt="{html.escape(name)}" class="granite-slab-thumb" loading="lazy" decoding="async" fetchpriority="low" width="400" height="400">\n'
            f"            </a>\n"
            f'            <div class="gallery-info">\n'
            f'              <h3><a href="{html.escape(detail_url)}" class="granite-slab-title-link">{html.escape(name)}</a></h3>\n'
            f'              <p class="granite-slab-thickness-badge" aria-label="Thickness">{html.escape(thickness_label)}</p>\n'
            f"              <p>{desc}</p>\n"
            f'              <a href="{html.escape(detail_url)}" class="granite-view-details">View details <span aria-hidden="true">→</span></a>\n'
            f"            </div>\n"
            f"          </article>"
        )

    cards_html = "\n".join(cards)
    with open(OUT) as f:
        content = f.read()

    pattern = r'(<div class="gallery-grid"[^>]*id="granite-gallery-grid"[^>]*>)(.*?)(</div>\s*\n\s*<p class="small")'
    replacement = rf"\1\n{cards_html}\n        \3"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    if new_content == content:
        pattern = r'(<div class="gallery-grid"[^>]*>)(.*?)(</div>\s*\n\s*<p class="small")'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(OUT, "w") as f:
        f.write(new_content)

    print(f"Updated {OUT} with {len(slabs)} granite slabs")


if __name__ == "__main__":
    main()
