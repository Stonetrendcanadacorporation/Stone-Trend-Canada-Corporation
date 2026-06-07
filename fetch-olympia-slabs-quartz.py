#!/usr/bin/env python3
"""Fetch quartz slab data from olympiatile.com aspen-quartz-series and build data/olympia-quartz.json."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

URL = "https://www.olympiatile.com/en/aspen-quartz-series-2.html"
DATA = Path(__file__).parent.parent / "data" / "olympia-quartz.json"

# SKU abbreviation -> full word (quartz slab names, incl. Aspen series)
SKU_WORDS = {
    "wht": "White", "wh": "White", "blk": "Black", "gr": "Grey", "gry": "Grey",
    "crem": "Cream", "crm": "Crema", "br": "Brown", "bl": "Blue",
    "grn": "Green", "ylw": "Yellow", "gld": "Gold", "pk": "Pink", "rd": "Red",
    "org": "Orange", "pl": "Polished", "hn": "Honed", "pol": "Polished",
    "grig": "Grigio", "bianco": "Bianco", "nero": "Nero", "tan": "Tan", "brown": "Brown",
    "blu": "Blue", "bia": "Bianco", "grg": "Grigio", "sil": "Silver",
    "aspen": "Aspen", "tribeca": "Tribeca", "athens": "Athens", "carrara": "Carrara",
    "ginger": "Ginger", "butter": "Butter", "brushed": "Brushed", "braken": "Braken",
    "caress": "Caress", "ivory": "Ivory", "pearl": "Pearl", "snow": "Snow",
    "calac": "Calacatta", "stat": "Statuario", "venat": "Venato",
}


def fetch_page():
    req = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def sku_to_name(sku):
    """Convert SKU to display name (quartz slab)."""
    if not sku:
        return None
    s = re.sub(r"^[A-Z0-9]{2,4}\.[A-Z]{0,3}\.", "", sku.upper())
    s = re.sub(r"\.?[23]CM$", "", s, flags=re.I)
    parts = re.split(r"[._\s]+", s)
    words = []
    for p in parts:
        if not p or p in ("PL", "HN", "VC", "CL", "MB"):
            continue
        low = p.lower()
        if low in SKU_WORDS:
            words.append(SKU_WORDS[low])
        else:
            words.append(p.capitalize())
    return " ".join(words) if words else None


def normalize_name(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def main():
    print("Fetching olympiatile.com aspen-quartz-series...")
    html = fetch_page()

    ids_2cm = set()
    ids_3cm = set()
    for m in re.finditer(r'"label":"(2CM|3CM)","products":\[([^\]]+)\]', html):
        label, ids_str = m.groups()
        ids = re.findall(r'"(\d+)"', ids_str)
        if "2" in label:
            ids_2cm.update(ids)
        else:
            ids_3cm.update(ids)

    # Product ID -> SKU (quartz: various prefixes e.g. QZ., QT., brand codes)
    id_to_sku = {}
    for m in re.findall(r'"(\d{5})":"([^"]+)"', html):
        pid, sku = m
        if ("2CM" in sku.upper() or "3CM" in sku.upper()) and "olympiatile" not in sku:
            id_to_sku[pid] = sku

    id_to_img = {}
    for pid in set(re.findall(r'"(\d{5})":\[\{', html)):
        block = re.search(rf'"{pid}":\[\{{[^\]]+\}}\]', html)
        if not block:
            continue
        obj = block.group(0)
        url = None
        for key in ("full", "img", "thumb"):
            m = re.search(rf'"{key}":"(https?:\\?/\\?/[^"]+)"', obj)
            if m:
                url = m.group(1).replace("\\/", "/")
                break
        if url and "olympiatile.com" in url and "placeholder" not in url.lower():
            id_to_img[pid] = url

    # If no 2CM/3CM split, treat all products as 2 cm
    if not ids_2cm and not ids_3cm:
        all_ids = set(id_to_sku.keys())
        ids_2cm = all_ids

    thickness_by_id = {}
    for pid in ids_2cm | ids_3cm:
        has2 = pid in ids_2cm
        has3 = pid in ids_3cm
        if has2 and has3:
            thickness_by_id[pid] = "2 cm, 3 cm"
        elif has2:
            thickness_by_id[pid] = "2 cm"
        else:
            thickness_by_id[pid] = "3 cm"

    name_thicknesses = {}
    name_best = {}
    for pid, sku in id_to_sku.items():
        if pid not in thickness_by_id:
            continue
        name = sku_to_name(sku)
        if not name:
            continue
        key = normalize_name(name)
        thick = thickness_by_id[pid]
        name_thicknesses.setdefault(key, set()).add(thick)
        img = id_to_img.get(pid)
        prev = name_best.get(key, {})
        if key not in name_best or (img and not prev.get("img")):
            name_best[key] = {"name": name, "sku": sku, "img": img or prev.get("img")}

    def slugify(n):
        s = re.sub(r"[^a-zA-Z0-9\s]", "", (n or "").lower())
        return re.sub(r"\s+", "_", s.strip())

    slabs = []
    seen_slugs = set()
    for key, thicknesses in name_thicknesses.items():
        if "2 cm, 3 cm" in thicknesses or ("2 cm" in thicknesses and "3 cm" in thicknesses):
            thick = "2 cm, 3 cm"
        elif "3 cm" in thicknesses:
            thick = "3 cm"
        else:
            thick = "2 cm"
        best = name_best.get(key, {})
        name = best.get("name")
        img = best.get("img")
        if not name or not img:
            continue
        slug = slugify(name)
        if slug in seen_slugs:
            slug = slug + "_quartz"
        seen_slugs.add(slug)
        slabs.append({
            "name": name,
            "code": best.get("sku"),
            "thickness": thick,
            "img_small": img,
            "img_large": img,
            "slug": slug,
            "url": URL,
            "format": "slab",
        })

    DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    print(f"Found {len(ids_2cm)} products in 2CM, {len(ids_3cm)} in 3CM")
    print(f"Wrote {len(slabs)} quartz slabs to {DATA}")


if __name__ == "__main__":
    main()
