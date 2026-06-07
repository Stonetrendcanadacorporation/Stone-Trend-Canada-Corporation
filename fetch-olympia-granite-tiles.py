#!/usr/bin/env python3
"""Fetch granite TILE data from olympiatile.com granite-series.html and append to data/olympia-granite.json with format 'tile'."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

URL = "https://www.olympiatile.com/en/granite-series.html"
DATA = Path(__file__).parent.parent / "data" / "olympia-granite.json"

SKU_WORDS = {
    "wht": "White", "blk": "Black", "gr": "Grey", "gry": "Grey", "bl": "Blue",
    "br": "Brown", "grn": "Green", "ylw": "Yellow", "gld": "Gold", "hn": "Honed",
    "basalt": "Basalt", "bia": "Bia", "col": "Col", "grg": "Grg", "sardo": "Sardo",
    "abl": "Abl", "blu": "Blue", "pearl": "Pearl", "galaxy": "Galaxy",
    "basal": "Basalt", "her": "Her", "bn": "BN", "n": "N",
}


def fetch_page():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def sku_to_tile_name(sku):
    """Convert tile SKU like GM.BIA.COL.1224 or GM.BLK.GALAXY.1212 to display name."""
    if not sku or "2CM" in sku.upper() or "3CM" in sku.upper() or ".SB." in sku.upper():
        return None
    s = sku.upper().replace("GM.", "").replace("GM_", "")
    # Remove size/spec suffixes: 1224, 12X12, 1818, 1236, HEX, HN, HN10MM, 0,4X1,9, 0112, etc.
    s = re.sub(r"\.?(\d{2,4}X?\d{2,4}|\d{4}|\d,\dX\d,\d|HEX|HN\d*MM?|HN\.?N?|\.N)$", "", s, flags=re.I)
    s = re.sub(r"\.(HN|N)$", "", s, flags=re.I)
    parts = re.split(r"[._\s]+", s)
    words = []
    for p in parts:
        if not p or p in ("HN", "N", "BN"):
            continue
        low = p.lower()
        if low in SKU_WORDS:
            words.append(SKU_WORDS[low])
        else:
            words.append(p.capitalize())
    return " ".join(words) if words else None


def slugify(n):
    s = re.sub(r"[^a-zA-Z0-9\s]", "", (n or "").lower())
    return re.sub(r"\s+", "_", s.strip())


def main():
    print("Fetching olympiatile.com granite-series (tiles)...")
    html = fetch_page()

    # Product ID -> SKU (tile SKUs only: no 2CM/3CM, no .SB.)
    id_to_sku = {}
    for m in re.findall(r'"(\d{5})":"(GM\.[^"]+)"', html):
        pid, sku = m
        if "2CM" in sku.upper() or "3CM" in sku.upper() or ".SB." in sku.upper():
            continue
        id_to_sku[pid] = sku

    id_to_img = {}
    for pid in set(re.findall(r'"(\d{5})":\[\{', html)):
        block = re.search(rf'"{pid}":\[\{{[^\]]+\}}\]', html)
        if not block:
            continue
        obj = block.group(0)
        for key in ("full", "img", "thumb"):
            m = re.search(rf'"{key}":"(https?:\\?/\\?/[^"]+)"', obj)
            if m:
                url = m.group(1).replace("\\/", "/")
                if "olympiatile.com" in url and "placeholder" not in url.lower():
                    id_to_img[pid] = url
                break

    # Build unique tile entries by base name (one card per stone, not per size)
    name_to_best = {}
    for pid, sku in id_to_sku.items():
        name = sku_to_tile_name(sku)
        if not name:
            continue
        key = re.sub(r"[^a-z0-9]", "", name.lower())
        img = id_to_img.get(pid)
        if key not in name_to_best or (img and not name_to_best[key].get("img")):
            name_to_best[key] = {"name": name, "sku": sku, "img": img or name_to_best.get(key, {}).get("img")}

    # Load existing granite data (slabs)
    if DATA.exists():
        with open(DATA) as f:
            existing = json.load(f)
        existing_slugs = {s.get("slug") for s in existing}
    else:
        existing = []
        existing_slugs = set()

    tiles = []
    for key, best in name_to_best.items():
        if not best.get("img"):
            continue
        name = best["name"]
        slug = slugify(name) + "_tile"
        if slug in existing_slugs:
            continue
        existing_slugs.add(slug)
        tiles.append({
            "name": name,
            "code": best.get("sku"),
            "thickness": "",
            "img_small": best["img"],
            "img_large": best["img"],
            "slug": slug,
            "url": URL,
            "format": "tile",
        })

    existing.extend(tiles)
    with open(DATA, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Added {len(tiles)} granite tiles to {DATA} (total entries: {len(existing)})")


if __name__ == "__main__":
    main()
