#!/usr/bin/env python3
"""Build Quebec series porcelain data - tile pics and description."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

URL = "https://www.olympiatile.com/en/quebec-series.html"
DATA = Path(__file__).parent.parent / "data" / "olympia-porcelain.json"

QUEBEC_DESCRIPTION = (
    'Dot-mounted unglazed porcelain in speckled and solid colours in 2"×2" format. '
    'Cove Base Inner (2"×2"), Cove Base Outer (2"×2"), and 2"×1" Pool nosing are available. '
    'The series also includes unglazed porcelain hexagon mosaics in a matte finish. '
    'Colours coordinate with the existing solid 2"×2" colours in the series. '
    'Trim pieces are available in select colours only; contact Stone Trend for availability.'
)

QUEBEC_COLOURS = [
    "Anthracite", "Anthracite Fleck", "Beige", "Arctic White", "Brown", "Driftwood",
    "Galaxy Speer", "Gold Granite", "Graphite", "Dark Grey", "Lake Blue", "Marble",
    "Mottled Grey", "Black", "Bone", "Egyptian Stone", "Pure White", "Pepper Quartz",
    "Sterling Grey", "Black Fleck", "Taupe Fleck", "White Granite",
]

SKU_PREFIX = "OD.QC.ATR"


def fetch_page(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9\s]", "", (name or "").lower())
    return re.sub(r"\s+", "_", s.strip()) or "quebec"


def extract_image_urls(html):
    """Extract full image URLs from JSON-like "full":"...ext" or "img":"...ext" (handles escaped slashes)."""
    urls = []
    idx = 0
    while True:
        i = html.find('"full":"', idx)
        if i < 0:
            i = html.find('"img":"', idx)
        if i < 0:
            break
        start = i + 8
        best = None
        for end_marker in ['.jpeg"', '.jpg"', '.webp"']:
            j = html.find(end_marker, start)
            if j > start and (best is None or j < best):
                best = j
        if best is not None:
            s = html[start : best + 1]
            s = s.replace("\\/", "/")
            if "olympiatile" in s and "catalog" in s:
                urls.append(s)
        idx = start + 1
        if len(urls) >= 35:
            break
    return urls


def path_after_cache(u):
    if "/cache/" in u:
        return u.split("/cache/")[-1]
    return u


def main():
    print("Fetching Quebec series for tile pics and swatches...")
    main_image = None
    swatch_urls = []
    try:
        html = fetch_page(URL)
        urls = extract_image_urls(html)
        decoded = [u for u in urls if "olympiatile" in u and "catalog/product" in u]

        # Main product image: first URL with od.qc.atr (e.g. 0101) - the large tile pic
        for u in decoded:
            p = path_after_cache(u)
            if "od.qc.atr" in p or "od_qc_atr" in p:
                main_image = u
                break
        if not main_image:
            main_image = "https://www.olympiatile.com/media/catalog/product/q/u/quebec.jpg"

        # Per-colour swatches: hash-named images only (exclude quebec_hex, od-qc, q/u/, o/d/)
        seen = set()
        for u in decoded:
            p = path_after_cache(u)
            if p in seen:
                continue
            if "quebec_hex" in p or "od-qc" in p or "od_qc" in p:
                continue
            if p.startswith("q/u/") or p.startswith("o/d/"):
                continue
            if "/" in p:
                name = p.split("/", 1)[-1]
            else:
                name = p
            if len(name) < 20:
                continue
            seen.add(p)
            swatch_urls.append(u)
        # Keep first 22 swatches (DOM order = colour order)
        swatch_urls = swatch_urls[: len(QUEBEC_COLOURS)]
        if len(swatch_urls) < len(QUEBEC_COLOURS):
            swatch_urls = swatch_urls + [main_image] * (len(QUEBEC_COLOURS) - len(swatch_urls))
    except Exception as e:
        print(f"  Error: {e}")

    if not swatch_urls and main_image:
        swatch_urls = [main_image] * len(QUEBEC_COLOURS)

    slabs = []
    for i, colour in enumerate(QUEBEC_COLOURS):
        name = f"Quebec - {colour}"
        slug = slugify(name)
        sku = f"{SKU_PREFIX}.{i+101:04d}.FS" if i < 9899 else f"{SKU_PREFIX}.FS"
        img = swatch_urls[i] if i < len(swatch_urls) else main_image
        slabs.append({
            "name": name,
            "code": sku,
            "thickness": "",
            "img_small": img,
            "img_large": img,
            "slug": slug,
            "url": URL,
            "format": "tile",
            "description": QUEBEC_DESCRIPTION,
            "colour": colour,
        })

    DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    print(f"  Built {len(slabs)} Quebec tiles with description and tile pics")
    print(f"  Main image: {main_image[:60]}..." if main_image else "  No main image")
    print(f"  Swatch images: {len(swatch_urls)} (one per colour)")


if __name__ == "__main__":
    main()
