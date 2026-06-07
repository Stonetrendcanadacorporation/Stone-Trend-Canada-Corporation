#!/usr/bin/env python3
"""
Expand porcelain series that currently have only one 'preview' entry into full variant entries.
For each series: fetches the series page, extracts Colour/variant options and gallery images,
then creates one product per variant with the matching image.
Removes the single preview entry and adds Series - Variant1, Series - Variant2, etc.
"""
import json
import re
import ssl
import time
import urllib.request
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-porcelain.json"
BASE_URL = "https://www.olympiatile.com/en"

# Slugs that are single-entry series we want to expand (from fetch-olympia-porcelain-all)
SERIES_TO_EXPAND = {
    "arkipro", "arkistone", "artwork", "ashima", "astrum", "baita", "beach", "biel", "blend",
    "design_industry", "district", "essential", "everlast", "gem", "gemme", "kerlite", "muse",
    "oxford", "palais", "pietra_di_stazzema", "portland", "rowan", "spectra", "tactile",
    "techstone", "the_room",
}

# Labels to skip when extracting colour/variant options
SKIP_LABELS = {
    "finish", "matte", "colour selection", "stock sizes", "edge type", "shade variation",
    "rectified", "non-rectified", "glazed porcelain", "unglazed porcelain", "coloured-base",
}

def fetch_page(url, timeout=25):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9\s\-]", "", (name or "").lower())
    return re.sub(r"[\s\-]+", "_", s.strip())


def extract_variant_labels(html):
    """
    Extract colour/variant option labels from page.
    Looks for "label":"X" in configurable options, skips sizes and meta labels.
    """
    labels = []
    for m in re.finditer(r'"label":"([^"]+)"', html):
        label = m.group(1).strip()
        if "\\\\" in label:
            label = label.replace("\\\\", "")
        label_lower = label.lower()
        if label_lower in SKIP_LABELS:
            continue
        if re.match(r"^[\d\s\"\'\`\\x]+$", label) or re.match(r"^\d+\s*[x×]\s*\d+", label):
            continue
        if "stock" in label_lower or "edge" in label_lower or "shade" in label_lower:
            continue
        if len(label) < 2 or len(label) > 50:
            continue
        if label not in labels:
            labels.append(label)
    return labels


def extract_images(html, max_urls=60):
    """Extract clean image URLs in order (no embedded JSON)."""
    urls = []
    idx = 0
    while len(urls) < max_urls:
        i = html.find('"full":"', idx)
        if i < 0:
            i = html.find('"img":"', idx)
        if i < 0:
            break
        start = i + 8
        for end_marker in ['.jpeg"', '.jpg"', '.png"', '.webp"']:
            j = html.find(end_marker, start)
            if j > start:
                raw = html[start : j + len(end_marker) - 1]
                raw = raw.replace("\\/", "/")
                if '"' in raw or "caption" in raw or "position" in raw:
                    break
                if "olympiatile.com" in raw and "catalog" in raw and "placeholder" not in raw.lower():
                    urls.append(raw)
                break
        idx = start + 1
    return urls


def extract_description(html):
    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if m:
        t = m.group(1).strip()
        if "product_addtocart" not in t and "HR0c" not in t and len(t) > 30:
            return t
    return "Porcelain series. Confirm description and specifications with Stone Trend."


def detect_format(html):
    html_lower = html.lower()
    if re.search(r"material\s+coloured-base|material\s+glazed|material\s+unglazed", html_lower):
        return "tile"
    if re.search(r"material\s+.*slab|large-format\s+slab", html_lower):
        return "slab"
    if "plank" in html_lower and "wood" in html_lower:
        return "slab"
    return "tile"


def main():
    if not DATA.exists():
        print("No", DATA)
        return

    with open(DATA) as f:
        entries = json.load(f)

    to_expand = []
    for i, e in enumerate(entries):
        slug = (e.get("slug") or "").strip()
        if slug in SERIES_TO_EXPAND:
            to_expand.append((i, e))

    if not to_expand:
        print("No single-entry series found to expand.")
        return

    to_expand.sort(key=lambda x: -x[0])
    for i, entry in to_expand:
        slug = entry.get("slug", "")
        url = entry.get("url", "")
        if not url:
            url_name = slug.replace("_", "-")
            url = f"{BASE_URL}/{url_name}-series.html"
        series_name = entry.get("name", slug.replace("_", " ").title())
        fmt = entry.get("format", "tile")
        product_type = entry.get("product_type", "tiles")
        desc = entry.get("description", "")

        print(f"Expanding {series_name}...", end=" ")
        html = fetch_page(url)
        if not html:
            print("fetch failed")
            time.sleep(1)
            continue

        variants = extract_variant_labels(html)
        images = extract_images(html)
        if not variants and not images:
            print("no variants or images")
            time.sleep(0.8)
            continue

        if not desc or len(desc) < 40:
            desc = extract_description(html)
        # Only use real colour/variant names – never create "Style N" placeholders
        if not variants and images:
            # No labels found: keep single entry with first image
            created = [{
                "name": series_name,
                "code": entry.get("code", series_name.upper().replace(" ", ".")),
                "thickness": entry.get("thickness", ""),
                "img_small": images[0] if images else "",
                "img_large": images[0] if images else "",
                "slug": slug,
                "url": url,
                "format": fmt,
                "description": desc,
                "product_type": product_type,
            }]
        elif variants and not images:
            images = [entry.get("img_small") or entry.get("img_large") or ""] * len(variants)
            created = []
            for j, (label, img) in enumerate(zip(variants, images)):
                name = f"{series_name} - {label}"
                var_slug = f"{slug}_{slugify(label)}"
                created.append({
                    "name": name,
                    "code": entry.get("code", series_name.upper().replace(" ", ".")),
                    "thickness": entry.get("thickness", ""),
                    "img_small": img or "",
                    "img_large": img or "",
                    "slug": var_slug,
                    "url": url,
                    "format": fmt,
                    "description": desc,
                    "product_type": product_type,
                    "colour": label,
                })
        else:
            # Match 1:1 – only create entries for real labels; use first n images (repeat last if needed)
            n = len(variants)
            if images:
                images_matched = (images + [images[-1]] * (n - len(images)))[:n]
            else:
                fallback = entry.get("img_small") or entry.get("img_large") or ""
                images_matched = [fallback] * n
            created = []
            for j, (label, img) in enumerate(zip(variants, images_matched)):
                name = f"{series_name} - {label}"
                var_slug = f"{slug}_{slugify(label)}"
                created.append({
                    "name": name,
                    "code": entry.get("code", series_name.upper().replace(" ", ".")),
                    "thickness": entry.get("thickness", ""),
                    "img_small": img or "",
                    "img_large": img or "",
                    "slug": var_slug,
                    "url": url,
                    "format": fmt,
                    "description": desc,
                    "product_type": product_type,
                    "colour": label,
                })
        entries = entries[:i] + created + entries[i+1:]
        print(f"{len(created)} variants")
        time.sleep(0.8)

    with open(DATA, "w") as f:
        json.dump(entries, f, indent=2)

    print(f"Done. Total entries: {len(entries)}")


if __name__ == "__main__":
    main()
