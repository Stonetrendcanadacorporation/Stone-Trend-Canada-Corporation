#!/usr/bin/env python3
"""Fetch slab data from Olympia Tile slab division marble series."""
import re
import json
import urllib.request
from pathlib import Path

BASE = "http://www.olympiatile-slabs.com"
MARBLE_LIST = "http://www.olympiatile-slabs.com/marble_all.asp"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")

def extract_slabs(html):
    """Extract slab links from marble_all.asp."""
    pattern = r'href="([a-z0-9_]+)\.asp">([^<]+)</a>'
    matches = re.findall(pattern, html)
    return [(slug, name.strip()) for slug, name in matches if slug not in ("about_us", "our_facility", "our_location", "contact_us", "default", "marble_home", "marble_all")]

def extract_slab_data(html, name):
    """Extract code, thickness, dimensions, and image from product page."""
    data = {"name": name, "code": None, "thickness": None, "dimensions": None, "img_small": None, "img_large": None}
    # Code: GM.SB.XXX.2CM
    m = re.search(r'Code[^<]*</td>\s*<td[^>]*>([^<]+)', html, re.I | re.S)
    if m:
        val = m.group(1).strip().replace("&nbsp;", "").strip()
        if val:
            data["code"] = val
    # Thickness
    m = re.search(r'Thickness[^<]*</td>\s*<td[^>]*>([^<]+)', html, re.I | re.S)
    if m:
        val = m.group(1).strip().replace("&nbsp;", "").strip()
        if val:
            data["thickness"] = val
    # Dimensions (if Olympia adds this field)
    for label in ("Dimensions", "Dimension", "Size", "Sizes"):
        m = re.search(rf'{re.escape(label)}[^<]*</td>\s*<td[^>]*>([^<]+)', html, re.I | re.S)
        if m:
            val = m.group(1).strip().replace("&nbsp;", "").strip()
            if val:
                data["dimensions"] = val
                break
    # Large image (main product)
    m = re.search(r'images/slabs/large/([^"]+\.jpg)', html)
    if m:
        data["img_large"] = f"{BASE}/images/slabs/large/{m.group(1)}"
    # Small image (from thumbnails)
    m = re.search(r'images/slabs/small/([^"]+\.jpg)', html)
    if m:
        data["img_small"] = f"{BASE}/images/slabs/small/{m.group(1)}"
    return data

def main():
    print("Fetching marble list...")
    html = fetch(MARBLE_LIST)
    slabs = extract_slabs(html)
    print(f"Found {len(slabs)} slabs")

    results = []
    for i, (slug, name) in enumerate(slabs):
        print(f"  {i+1}. {name}...")
        try:
            page = fetch(f"{BASE}/{slug}.asp")
            data = extract_slab_data(page, name)
            data["slug"] = slug
            data["url"] = f"{BASE}/{slug}.asp"
            if data["img_large"] or data["img_small"]:
                results.append(data)
        except Exception as e:
            print(f"    Error: {e}")
        if (i + 1) % 20 == 0:
            print(f"  ... progress: {i+1}/{len(slabs)}")

    out = Path(__file__).parent.parent / "data" / "olympia-marble.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} slabs to {out}")

if __name__ == "__main__":
    main()
