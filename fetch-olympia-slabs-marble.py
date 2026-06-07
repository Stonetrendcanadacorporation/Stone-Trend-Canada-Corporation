#!/usr/bin/env python3
"""Fetch slab thickness (2cm, 3cm) from olympiatile.com slabs-marble-series and merge with existing data."""
import json
import re
import ssl
import urllib.request
from pathlib import Path

URL = "https://www.olympiatile.com/en/slabs-marble-series.html"
DATA = Path(__file__).parent.parent / "data" / "olympia-marble.json"

# SKU abbreviation -> word (common patterns)
SKU_WORDS = {
    "wht": "White", "wh": "White", "blk": "Black", "gr": "Grey", "gry": "Grey",
    "crem": "Cream", "crm": "Crema", "br": "Brown", "bl": "Blue", "grn": "Green",
    "ylw": "Yellow", "gld": "Gold", "pk": "Pink", "rd": "Red", "org": "Orange",
    "pl": "Polished", "hn": "Honed", "vc": "Vein Cut", "cls": "CLS", "mb": "MB",
    "pol": "Polished", "mar": "Marfil", "marq": "Marquina", "cal": "Calacatta",
    "stat": "Statuario", "carr": "Carrara", "arab": "Arabescato", "braz": "Brazilian",
    "emp": "Emperador", "fant": "Fantastico", "negro": "Negro", "b": "Bianco",
    "namibia": "Namibia", "grig": "Grigio", "rosso": "Rosso", "rojo": "Rojo",
    "azul": "Azul", "verde": "Verde", "bianco": "Bianco", "nero": "Nero",
    "ven": "Venato", "vein": "Veined", "linc": "Lincoln", "swt": "Sweet",
    "lf": "Leather", "latt": "Latte", "via": "Via", "soap": "Soap",
    "jolie": "Jolie", "val": "Valley", "gld": "Gold", "v": "Vein",
}


def fetch_page():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def sku_to_name(sku):
    """Convert SKU like GM.SB.AFYON.WHT.2CM to 'Afyon White'."""
    if not sku:
        return None
    s = sku.upper().replace("GM.SB.", "").replace("GM_SB_", "")
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
    """Normalize for matching."""
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def main():
    print("Fetching olympiatile.com slabs-marble-series...")
    html = fetch_page()

    # Extract thickness options: "label":"2CM","products":["18604",...]
    ids_2cm = set()
    ids_3cm = set()
    for m in re.finditer(r'"label":"(2CM|3CM)","products":\[([^\]]+)\]', html):
        label, ids_str = m.groups()
        ids = re.findall(r'"(\d+)"', ids_str)
        if "2" in label:
            ids_2cm.update(ids)
        else:
            ids_3cm.update(ids)

    # Extract product ID -> SKU: "18604":"GM.SB.AFYON.WHT.2CM"
    id_to_sku = {}
    for m in re.findall(r'"(\d{5})":"(GM\.[^"]+)"', html):
        pid, sku = m
        if "GM." in sku and ("2CM" in sku.upper() or "3CM" in sku.upper()):
            id_to_sku[pid] = sku

    # Extract product ID -> image (use "full" for high-res, fallback to "img" then "thumb")
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

    # Build thickness per product ID
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

    # Build mapping: normalized_name -> {thickness, sku, img}
    # Aggregate by name: if same marble has 2cm and 3cm variants, combine
    name_thicknesses = {}  # key -> set of thicknesses
    name_best = {}  # key -> best sku, img
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

    name_to_specs = {}
    for key, thicknesses in name_thicknesses.items():
        if "2 cm, 3 cm" in thicknesses or ("2 cm" in thicknesses and "3 cm" in thicknesses):
            thick = "2 cm, 3 cm"
        elif "3 cm" in thicknesses:
            thick = "3 cm"
        else:
            thick = "2 cm"
        best = name_best.get(key, {})
        name_to_specs[key] = {
            "name": best.get("name"),
            "thickness": thick,
            "sku": best.get("sku"),
            "img": best.get("img"),
        }

    # Add slugs for new slabs
    def slugify(n):
        s = re.sub(r"[^a-zA-Z0-9\s]", "", (n or "").lower())
        return re.sub(r"\s+", "_", s.strip())

    print(f"  Found {len(ids_2cm)} products in 2CM, {len(ids_3cm)} in 3CM")
    print(f"  Mapped {len(name_to_specs)} marble types with thickness")

    # Load existing data
    with open(DATA) as f:
        slabs = json.load(f)

    updated = 0
    for s in slabs:
        if s.get("format") == "tile":
            continue
        name = s.get("name", "").replace("&quot;", '"').replace("&nbsp;", " ").strip()
        key = normalize_name(name)
        specs = name_to_specs.get(key)
        if not specs and len(key) >= 5:
            for spec_key, spec_val in name_to_specs.items():
                if len(spec_key) >= 5 and (key in spec_key or spec_key in key):
                    specs = spec_val
                    break
        if specs:
            s["thickness"] = specs["thickness"]
            if specs.get("sku"):
                s["code"] = specs["sku"]
            if specs.get("img"):
                s["img_large"] = specs["img"]
                s["img_small"] = specs["img"]
            updated += 1

    # Add new slabs from olympiatile.com not in our data
    existing_keys = {normalize_name(s.get("name", "").replace("&quot;", '"').replace("&nbsp;", " ").strip()) for s in slabs}
    existing_slugs = {s.get("slug") for s in slabs}
    added = 0
    for key, specs in name_to_specs.items():
        if key in existing_keys:
            continue
        name = specs.get("name")
        if not name or not specs.get("img"):
            continue
        slug = slugify(name)
        if slug in existing_slugs:
            continue
        while slug in existing_slugs:
            slug = slug + "_slab"
        existing_slugs.add(slug)
        slabs.append({
            "name": name,
            "code": specs.get("sku"),
            "thickness": specs["thickness"],
            "img_small": specs["img"],
            "img_large": specs["img"],
            "slug": slug,
            "url": URL,
            "format": "slab",
        })
        added += 1

    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    print(f"Updated thickness for {updated} slabs, added {added} new slabs from olympiatile.com")


if __name__ == "__main__":
    main()
