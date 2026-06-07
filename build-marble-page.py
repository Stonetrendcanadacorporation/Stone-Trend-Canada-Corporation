#!/usr/bin/env python3
"""Build marble-slabs.html from marble JSON data."""
import json
import html
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-marble.json"
OUT = Path(__file__).parent.parent / "marble-slabs.html"

def fix_name(name):
    """Fix HTML entities in slab names."""
    if not name:
        return name
    s = html.unescape(name)
    s = s.replace("&nbsp;", " ").strip()
    return s

def clean_spec(val):
    """Clean &nbsp; and empty specs."""
    if not val or val.strip() in ("&nbsp;", ""):
        return None
    return val.replace("&nbsp;", " ").strip()

def get_description(s):
    """Generate short description from slab name, colours, and specs."""
    name = fix_name(s.get("name", ""))
    colors = s.get("colors", [])
    code = clean_spec(s.get("code"))
    thickness = clean_spec(s.get("thickness"))
    img = s.get("img_large") or s.get("img_small") or ""
    # Infer 2 cm from image filename if not in data
    if not thickness and img and "2CM" in img.upper():
        thickness = "2 cm"
    if not thickness:
        thickness = "2 cm"  # standard for marble slabs
    color_str = ", ".join(colors).replace("multicolour", "multi-tone")
    if len(colors) >= 2 and "multicolour" not in colors:
        color_str = color_str + " tones"
    elif len(colors) == 1:
        color_str = color_str + " marble"
    # Build description
    parts = [f"{color_str.capitalize()} with natural veining and movement."]
    parts.append(f"Available in {thickness}.")
    parts.append("Suitable for countertops, vanities, and feature applications.")
    return " ".join(parts)

# Curated slugs for first 2 rows (8 cards) – most visually striking marbles
FEATURED_FIRST = [
    "calacatta", "statuario", "bianco_carrara", "nero_marquina",
    "crema_marfil", "calacatta_arabescato", "breccia_paradiso", "breche_de_vendome",
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

    def get_thickness_filter(slab):
        """Return space-separated thickness values for filtering: 2cm, 3cm, or both."""
        if slab.get("format") == "tile":
            return ""
        t = str(slab.get("thickness", "") or "").lower().replace(" ", "")
        vals = []
        if "2cm" in t or ("2" in t and "cm" in t):
            vals.append("2cm")
        if "3cm" in t or ("3" in t and "cm" in t):
            vals.append("3cm")
        return " ".join(vals) if vals else "2cm"  # default slabs to 2cm

    cards = []
    for i, s in enumerate(slabs):
        name = fix_name(s["name"])
        img = s.get("img_large") or s.get("img_small") or ""
        desc = get_description(s)
        delay = (i % 3) * 60  # Stagger animation
        category = s.get("category", "light")
        colors = s.get("colors", [])
        colors_attr = " ".join(html.escape(c) for c in colors)
        thickness_attr = get_thickness_filter(s)
        slug = s.get("slug", "")
        detail_url = f"marble/{slug}.html" if slug else ""
        cards.append(f'''          <article class="gallery-item marble-slab-card" data-animate="fade-up" data-animate-delay="{delay}" data-category="{html.escape(category)}" data-colors="{colors_attr}" data-thickness="{html.escape(thickness_attr)}">
            <a href="{html.escape(detail_url)}" class="marble-slab-image-link" aria-label="View {html.escape(name)} details">
              <img src="{html.escape(img)}" alt="{html.escape(name)}" class="marble-slab-thumb" loading="lazy" decoding="async" fetchpriority="low" width="400" height="400">
            </a>
            <div class="gallery-info">
              <h3><a href="{html.escape(detail_url)}" class="marble-slab-title-link">{html.escape(name)}</a></h3>
              <p>{desc}</p>
              <a href="{html.escape(detail_url)}" class="marble-view-details">View details <span aria-hidden="true">→</span></a>
            </div>
          </article>''')

    cards_html = "\n".join(cards)

    # Read template (the marble-slabs.html structure) and inject cards
    with open(OUT) as f:
        content = f.read()

    # Replace the gallery grid section
    import re
    pattern = r'(<div class="gallery-grid"[^>]*>)(.*)(</div>\s*\n\s*<p class="small")'
    replacement = rf'\1\n{cards_html}\n        \3'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Update section header (remove any Olympia references)
    new_header = "This catalogue illustrates a selection of marble slabs available through Stone Trend. Exact veining, movement, and availability are reviewed with our team during the selection process."
    old_patterns = [
        "Marble slabs from Olympia Tile's Marble Series. This catalogue illustrates a selection of natural stone options available through Stone Trend. Exact veining, movement, and availability are reviewed with our team during the selection process.",
        "This catalogue illustrates a sampling of marble looks often coordinated on Stone Trend projects. Exact\n            veining, movement, and availability are reviewed with our team during the selection process.",
    ]
    for old in old_patterns:
        if old in new_content:
            new_content = new_content.replace(old, new_header)
            break

    with open(OUT, "w") as f:
        f.write(new_content)

    print(f"Updated {OUT} with {len(slabs)} marble slabs")

if __name__ == "__main__":
    main()
