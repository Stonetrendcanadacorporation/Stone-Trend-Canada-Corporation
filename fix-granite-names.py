#!/usr/bin/env python3
"""Expand abbreviated granite names in data/olympia-granite.json to full titles (slugs and images unchanged)."""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-granite.json"

# Whole-word abbreviation (lowercase) -> full display name
NAME_EXPANSIONS = {
    "bwn": "Brown", "coff": "Coffee", "cale": "Calcutta", "plat": "Platino",
    "bia": "Bianco", "col": "Colonnata", "grg": "Grigio", "prl": "Pearl",
    "bord": "Border", "gal": "Galaxy", "saph": "Sapphire", "sib": "Siberian",
    "sil": "Silver", "trop": "Tropical", "typh": "Typhoon", "bah": "Bahia",
    "alp": "Alpine", "hima": "Himalaya", "imp": "Imperial", "nro": "Nero",
    "caled": "Caledonia", "ornam": "Ornamental", "abl": "Absolute", "ang": "Angola",
    "mah": "Mahal", "latt": "Latte", "lab": "Labrador", "an": "Antique",
    "mar": "Marquina", "belved": "Belvedere", "nig": "Negro", "mis": "Mississippi",
    "ven": "Venice", "nia": "Nevada", "roma": "Roman", "torr": "Torrent",
    "bwm": "Brown", "cor": "Coral", "dia": "Diamond", "arr": "Arrow",
    "cri": "Cristal", "mos": "Mosaic", "came": "Carmel", "ivo": "Ivory",
    "kod": "Kodiak", "blu": "Blue", "g": "Grigio", "sc": "SC", "lf": "Leather Finish",
    "fl": "FL", "ab": "Absolute", "am": "American", "cam": "Cambrian",
}


def expand_name(name):
    if not name or not name.strip():
        return name
    result = name
    for abbr, full in NAME_EXPANSIONS.items():
        # Whole-word replacement (case-insensitive)
        pattern = re.compile(r"\b" + re.escape(abbr) + r"\b", re.I)
        result = pattern.sub(full, result)
    return result


def main():
    with open(DATA) as f:
        items = json.load(f)
    updated = 0
    for item in items:
        old_name = item.get("name", "")
        new_name = expand_name(old_name)
        if new_name != old_name:
            item["name"] = new_name
            updated += 1
    with open(DATA, "w") as f:
        json.dump(items, f, indent=2)
    print(f"Expanded {updated} granite names to full titles in {DATA}")


if __name__ == "__main__":
    main()
