#!/usr/bin/env python3
"""Fetch AEQUA series porcelain slabs from olympiatile.com/en/aequa-series.html and append to data/olympia-porcelain.json."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

URL = "https://www.olympiatile.com/en/aequa-series.html"
DATA = Path(__file__).parent.parent / "data" / "olympia-porcelain.json"

# Product ID -> (SKU, colour name) from page: VE.AQ.CAS.0832 = Castor, CIR = Cirrus, NIX = Nix, TUR = Tur
AEQUA_PRODUCTS = {
    "20390": ("VE.AQ.CAS.0832", "Castor"),
    "20392": ("VE.AQ.CIR.0832", "Cirrus"),
    "20393": ("VE.AQ.NIX.0832", "Nix"),
    "20394": ("VE.AQ.TUR.0832", "Tur"),
}

AEQUA_DESCRIPTION = (
    "Natural wood-look coloured-base porcelain planks with a contemporary colour palette. "
    "Suitable for floors, walls, and feature applications."
)


def fetch_page():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def extract_image(html, pid):
    block = re.search(rf'"{pid}":\[\{{[^\]]+\}}\]', html)
    if not block:
        return None
    obj = block.group(0)
    for key in ("full", "img", "thumb"):
        m = re.search(rf'"{key}":"(https?:\\?/\\?/[^"]+)"', obj)
        if m:
            url = m.group(1).replace("\\/", "/")
            if "olympiatile.com" in url and "placeholder" not in url.lower():
                return url
    return None


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9\s]", "", (name or "").lower())
    return re.sub(r"\s+", "_", s.strip())


def main():
    print("Fetching AEQUA series (porcelain slabs)...")
    html = fetch_page()

    existing = []
    existing_slugs = set()
    if DATA.exists():
        with open(DATA) as f:
            existing = json.load(f)
        existing_slugs = {s.get("slug") for s in existing}

    slabs = []
    for pid, (sku, colour) in AEQUA_PRODUCTS.items():
        name = f"Aequa - {colour}"
        slug = f"aequa_{slugify(colour)}"
        if slug in existing_slugs:
            continue
        existing_slugs.add(slug)
        img = extract_image(html, pid)
        slabs.append({
            "name": name,
            "code": sku,
            "thickness": "8 mm",
            "img_small": img or "",
            "img_large": img or "",
            "slug": slug,
            "url": URL,
            "format": "slab",
            "description": AEQUA_DESCRIPTION,
            "colour": colour,
            "product_type": "slabs",
        })

    existing.extend(slabs)
    with open(DATA, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Added {len(slabs)} AEQUA porcelain slabs to {DATA} (total: {len(existing)})")


if __name__ == "__main__":
    main()
