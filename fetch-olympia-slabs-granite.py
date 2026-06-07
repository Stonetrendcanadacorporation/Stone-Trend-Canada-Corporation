#!/usr/bin/env python3
"""Fetch granite slab data from olympiatile.com slabs-granite-series and build data/olympia-granite.json."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

URL = "https://www.olympiatile.com/en/slabs-granite-series.html"
DATA = Path(__file__).parent.parent / "data" / "olympia-granite.json"

# SKU abbreviation -> full word (use full names, not short forms)
SKU_WORDS = {
    "wht": "White", "wh": "White", "blk": "Black", "gr": "Grey", "gry": "Grey",
    "amb": "Ambra", "crem": "Cream", "crm": "Crema", "br": "Brown", "bl": "Blue",
    "grn": "Green", "ylw": "Yellow", "gld": "Gold", "pk": "Pink", "rd": "Red",
    "org": "Orange", "pl": "Polished", "hn": "Honed", "vc": "Vein Cut", "cls": "CLS",
    "mb": "MB", "pol": "Polished", "b": "Bianco", "namibia": "Namibia", "grig": "Grigio",
    "rosso": "Rosso", "rojo": "Rojo", "azul": "Azul", "verde": "Verde", "bianco": "Bianco",
    "nero": "Nero", "charcoal": "Charcoal", "salt": "Salt", "pepper": "Pepper",
    "snow": "Snow", "tan": "Tan", "brown": "Brown",
    # Granite full-name expansions (no short forms)
    "bwn": "Brown", "coff": "Coffee", "cale": "Calcutta", "plat": "Platino",
    "blu": "Blue", "bia": "Bianco", "col": "Colonnata", "grg": "Grigio", "sardo": "Sardo",
    "prl": "Pearl", "bord": "Border", "gal": "Galaxy", "saph": "Sapphire", "sib": "Siberian",
    "sil": "Silver", "trop": "Tropical", "typh": "Typhoon", "bah": "Bahia", "alp": "Alpine",
    "hima": "Himalaya", "imp": "Imperial", "nro": "Nero", "caled": "Caledonia",
    "ornam": "Ornamental", "abl": "Absolute", "ang": "Angola", "mah": "Mahal",
    "latt": "Latte", "lab": "Labrador", "an": "Antique", "mar": "Marquina",
    "belved": "Belvedere", "nig": "Negro", "mis": "Mississippi", "ven": "Venice",
    "nia": "Nevada", "roma": "Roman", "torr": "Torrent", "bwm": "Brown",
    "cor": "Coral", "dia": "Diamond", "arr": "Arrow", "bbk": "BBK", "cri": "Cristal",
    "mos": "Mosaic", "came": "Carmel", "ivo": "Ivory", "kod": "Kodiak",
}


def fetch_page():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def sku_to_name(sku):
    """Convert SKU like GM.SB.AGATA.2CM or GG.SB.xxx.2CM to display name."""
    if not sku:
        return None
    s = sku.upper().replace("GM.SB.", "").replace("GM_SB_", "").replace("GG.SB.", "").replace("GG_SB_", "")
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
    print("Fetching olympiatile.com slabs-granite-series...")
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

    # Product ID -> SKU (GM. or GG. for granite)
    id_to_sku = {}
    for m in re.findall(r'"(\d{5})":"(G[MG]\.[^"]+)"', html):
        pid, sku = m
        if "2CM" in sku.upper() or "3CM" in sku.upper():
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
            slug = slug + "_granite"
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
    print(f"Wrote {len(slabs)} granite slabs to {DATA}")


if __name__ == "__main__":
    main()
