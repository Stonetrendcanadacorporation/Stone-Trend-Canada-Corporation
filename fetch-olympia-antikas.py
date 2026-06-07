#!/usr/bin/env python3
"""Fetch ANTIKAS series (glazed porcelain tiles) from olympiatile.com – collection with Bianco, Grigio, Beige."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

URL = "https://www.olympiatile.com/en/antikas-series.html"
DATA = Path(__file__).parent.parent / "data" / "olympia-porcelain.json"

# Antikas is a collection: colour options per Olympia (Bianco = white, Grigio = grey, Beige = cream/tan)
ANTIKAS_COLOURS = ["Bianco", "Grigio", "Beige"]

ANTIKAS_DESCRIPTION = (
    "Glazed porcelain series with a worn stone look. "
    "Shade variation V-2, non-rectified edge. "
    "Suitable for floors, walls, residential and commercial use."
)


def fetch_page():
    req = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def extract_image_urls(html):
    """Extract full image URLs; ensure they end with .jpeg or .jpg (fix truncated URLs)."""
    urls = []
    idx = 0
    while True:
        i = html.find('"full":"', idx)
        if i < 0:
            i = html.find('"img":"', idx)
        if i < 0:
            break
        start = i + 8
        # Find end of URL: .jpeg" or .jpg" (include extension)
        for end_marker in ['.jpeg"', '.jpg"', '.webp"']:
            j = html.find(end_marker, start)
            if j > start:
                raw = html[start : j + len(end_marker) - 1]
                raw = raw.replace("\\/", "/")
                if "olympiatile" in raw and "catalog" in raw and "placeholder" not in raw.lower():
                    urls.append(raw)
                break
        idx = start + 1
        if len(urls) >= 10:
            break
    return urls


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9\s]", "", (name or "").lower())
    return re.sub(r"\s+", "_", s.strip()) or "antikas"


def main():
    print("Fetching ANTIKAS series (Bianco, Grigio, Beige)...")
    html = fetch_page()
    urls = extract_image_urls(html)
    # Use first valid image for all if we don't have per-colour; ensure valid extension
    base_img = ""
    for u in urls:
        if u.endswith((".jpeg", ".jpg", ".webp")):
            base_img = u
            break
    if not base_img and urls:
        base_img = urls[0]
        if base_img.rstrip().endswith("."):
            base_img = base_img.rstrip() + "jpeg"

    existing = []
    if DATA.exists():
        with open(DATA) as f:
            existing = json.load(f)
    # Remove old single "antikas" entry; keep only non-antikas or antikas_* collection entries
    existing = [s for s in existing if s.get("slug") != "antikas"]
    existing_slugs = {s.get("slug") for s in existing}

    added = []
    for i, colour in enumerate(ANTIKAS_COLOURS):
        name = f"Antikas - {colour}"
        slug = f"antikas_{slugify(colour)}"
        if slug in existing_slugs:
            continue
        existing_slugs.add(slug)
        # If we have multiple images, use i-th for this colour; else same image
        img = urls[i] if i < len(urls) and urls[i].endswith((".jpeg", ".jpg", ".webp")) else base_img
        if img and img.rstrip().endswith("."):
            img = img.rstrip() + "jpeg"
        entry = {
            "name": name,
            "code": f"ANTIKAS.{colour.upper()}" if colour else "ANTIKAS",
            "thickness": "",
            "img_small": img or "",
            "img_large": img or "",
            "slug": slug,
            "url": URL,
            "format": "tile",
            "description": ANTIKAS_DESCRIPTION,
            "colour": colour,
            "product_type": "tiles",
        }
        existing.append(entry)
        added.append(name)

    DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA, "w") as f:
        json.dump(existing, f, indent=2)

    if added:
        print(f"  Added Antikas collection: {', '.join(added)} (total entries: {len(existing)})")
    else:
        print("  Antikas collection (Bianco, Grigio, Beige) already present.")


if __name__ == "__main__":
    main()
