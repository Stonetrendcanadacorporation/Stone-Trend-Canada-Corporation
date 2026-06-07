#!/usr/bin/env python3
"""
Fetch all porcelain series from Olympia Tile index that we don't already have.
Uses data/olympia-porcelain-series-to-fetch.txt for series names.
Skips: quebec, aequa, antikas (already in site), apini (removed).
For each series: fetches series page, extracts description/specs/material, images;
categorizes as tile or slab; appends to data/olympia-porcelain.json.
"""
import json
import re
import ssl
import time
import urllib.request
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-porcelain.json"
SERIES_LIST = Path(__file__).parent.parent / "data" / "olympia-porcelain-series-to-fetch.txt"
BASE_URL = "https://www.olympiatile.com/en"

# Slug prefixes we already have or skip
SKIP_PREFIXES = {"quebec", "aequa", "antikas", "apini"}


def fetch_page(url, timeout=25):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9\s\-]", "", (name or "").lower())
    return re.sub(r"[\s\-]+", "_", s.strip()) or "porcelain"


def extract_description(html):
    """Get series description from meta or first substantial paragraph."""
    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if m:
        t = m.group(1).strip()
        if "product_addtocart" not in t and "HR0c" not in t and len(t) > 30:
            return t
    m = re.search(r'<meta property="og:description" content="([^"]+)"', html)
    if m:
        t = m.group(1).strip()
        if "product_addtocart" not in t and "HR0c" not in t and len(t) > 30:
            return t
    # Look for paragraph after product title / description area (avoid form/script garbage)
    for pat, grp in [
        (r"Description[^>]*>[\s\S]*?([A-Z][^<]{60,400})", 1),
        (r"(Arkipro combines the natural beauty[\s\S]*?\.)\s*", 1),
        (r"(Glazed porcelain[\s\S]*?\.)\s*", 1),
        (r"(Unglazed porcelain[\s\S]*?\.)\s*", 1),
    ]:
        m = re.search(pat, html)
        if m:
            t = re.sub(r"\s+", " ", m.group(grp).strip())[:500]
            if "product_addtocart" not in t and "class=" not in t and len(t) > 40:
                return t
    return "Porcelain series. Confirm description and specifications with Stone Trend."


def detect_format(html):
    """Return 'tile' or 'slab' from page content. Prefer Material line over nav."""
    html_lower = html.lower()
    # Material line usually says Coloured-Base, Glazed, Unglazed (tiles) or Slab
    if re.search(r"material\s+coloured-base|material\s+glazed|material\s+unglazed", html_lower):
        return "tile"
    if re.search(r"material\s+.*slab|large-format\s+slab", html_lower):
        return "slab"
    if "plank" in html_lower and "wood" in html_lower:
        return "slab"
    # Default: porcelain under tile-stone is usually tile
    return "tile"


def extract_images(html, max_urls=15):
    """Extract clean image URLs (no embedded JSON)."""
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


def get_series_list():
    if not SERIES_LIST.exists():
        return []
    names = []
    for line in open(SERIES_LIST):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = line.split("#")[0].strip().lower()
        if name and name not in names:
            names.append(name)
    return names


def main():
    series_names = get_series_list()
    if not series_names:
        print("No series list at", SERIES_LIST)
        return

    existing = []
    existing_slugs = set()
    if DATA.exists():
        with open(DATA) as f:
            existing = json.load(f)
        existing_slugs = {s.get("slug") for s in existing}
        for s in existing:
            slug = s.get("slug", "")
            if "_" in slug:
                prefix = slug.split("_")[0]
                existing_slugs.add(prefix)

    added = []
    for name in series_names:
        # Normalize to URL segment (e.g. design-industry -> design-industry)
        url_name = name.replace("_", "-")
        prefix = name.replace("-", "_").split("_")[0]
        if prefix in SKIP_PREFIXES:
            continue
        # Single series entry slug e.g. arkipro (not arkipro_1)
        slug = slugify(name.replace("-", " "))
        if slug in existing_slugs:
            continue
        # Also skip if we already have any slug starting with this series
        if any(s.startswith(slug + "_") or s == slug for s in existing_slugs):
            continue

        url = f"{BASE_URL}/{url_name}-series.html"
        print(f"Fetching {url_name}...", end=" ")
        html = fetch_page(url)
        if not html:
            print("failed")
            time.sleep(1)
            continue

        desc = extract_description(html)
        fmt = detect_format(html)
        product_type = "tiles" if fmt == "tile" else "slabs"
        images = extract_images(html)
        img = images[0] if images else ""

        title_name = " ".join(w.capitalize() for w in url_name.split("-"))
        entry = {
            "name": title_name,
            "code": title_name.upper().replace(" ", "."),
            "thickness": "",
            "img_small": img,
            "img_large": img,
            "slug": slug,
            "url": url,
            "format": fmt,
            "description": desc,
            "product_type": product_type,
        }
        existing.append(entry)
        existing_slugs.add(slug)
        added.append(title_name)
        print("ok")
        time.sleep(0.8)

    DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"\nAdded {len(added)} series. Total entries: {len(existing)}")
    if added:
        print("New:", ", ".join(added[:20]), "..." if len(added) > 20 else "")


if __name__ == "__main__":
    main()
