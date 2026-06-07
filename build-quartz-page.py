#!/usr/bin/env python3
"""Build quartz-slabs.html from quartz JSON data."""
import json
import html
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-quartz.json"
OUT = Path(__file__).parent.parent / "quartz-slabs.html"


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
    colors = s.get("colors", [])
    color_str = ", ".join(colors).replace("multicolour", "multi-tone")
    if len(colors) >= 2 and "multicolour" not in colors:
        color_str = color_str + " tones"
    elif len(colors) == 1:
        color_str = color_str + " quartz"
    thickness = clean_spec(s.get("thickness")) or "2 cm"
    parts = [f"{color_str.capitalize()} engineered quartz with consistent colour and durability."]
    parts.append(f"Available in {thickness}.")
    parts.append("Suitable for countertops, vanities, and feature applications.")
    return " ".join(parts)


def get_thickness_filter(slab):
    t = str(slab.get("thickness", "") or "").lower().replace(" ", "")
    vals = []
    if "2cm" in t or ("2" in t and "cm" in t):
        vals.append("2cm")
    if "3cm" in t or ("3" in t and "cm" in t):
        vals.append("3cm")
    return " ".join(vals) if vals else "2cm"


def get_thickness_label(slab):
    raw = clean_spec(slab.get("thickness")) or "2 cm"
    raw_lower = raw.lower().replace(" ", "")
    if "2" in raw_lower and "3" in raw_lower:
        return "2 cm & 3 cm"
    if "3" in raw_lower and "cm" in raw_lower:
        return "3 cm"
    return "2 cm"


def main():
    with open(DATA) as f:
        slabs = json.load(f)

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
        slug = s.get("slug", "")
        detail_url = f"quartz/{slug}.html" if slug else ""
        cards.append(
            f'          <article class="gallery-item quartz-slab-card" data-animate="fade-up" data-animate-delay="{delay}" '
            f'data-category="{html.escape(category)}" data-colors="{colors_attr}" data-thickness="{html.escape(thickness_attr)}" data-format="slab">\n'
            f'            <a href="{html.escape(detail_url)}" class="quartz-slab-image-link" aria-label="View {html.escape(name)} details">\n'
            f'              <img src="{html.escape(img)}" alt="{html.escape(name)}" class="quartz-slab-thumb" loading="lazy" width="400" height="400">\n'
            f"            </a>\n"
            f'            <div class="gallery-info">\n'
            f'              <h3><a href="{html.escape(detail_url)}" class="quartz-slab-title-link">{html.escape(name)}</a></h3>\n'
            f'              <p class="quartz-slab-thickness-badge" aria-label="Thickness">{html.escape(thickness_label)}</p>\n'
            f"              <p>{desc}</p>\n"
            f'              <a href="{html.escape(detail_url)}" class="quartz-view-details">View details <span aria-hidden="true">→</span></a>\n'
            f"            </div>\n"
            f"          </article>"
        )

    cards_html = "\n".join(cards)
    with open(OUT) as f:
        content = f.read()

    pattern = r'(<div class="gallery-grid"[^>]*id="quartz-gallery-grid"[^>]*>)(.*?)(</div>\s*\n\s*<p class="small")'
    replacement = rf"\1\n{cards_html}\n        \3"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    if new_content == content:
        pattern = r'(<div class="gallery-grid"[^>]*>)(.*?)(</div>\s*\n\s*<p class="small")'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(OUT, "w") as f:
        f.write(new_content)

    print(f"Updated {OUT} with {len(slabs)} quartz slabs")


if __name__ == "__main__":
    main()
