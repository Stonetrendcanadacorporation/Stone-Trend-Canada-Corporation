#!/usr/bin/env python3
"""Add color and category (shade) metadata to porcelain data based on name and colour."""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-porcelain.json"

# Match product name and variant colour; order can matter (more specific first)
COLOR_RULES = [
    # White / light
    (r"\b(invisible white|ivory|arctic white|pure white|bianco|blanco|snow|ice white)\b", "white"),
    (r"\b(white granite|white|pearl|calacatta)\b", "white"),
    # Black / dark
    (r"\b(black|nero|noir|negro|carbone)\b", "black"),
    (r"\b(anthracite|graphite|grafito|charcoal|dark grey|galaxy speer)\b", "grey"),
    (r"\b(grey|gray|grigio|gris|silver|mottled grey|cenere|rupe|arena|libra)\b", "grey"),
    (r"\b(sterling grey|light grey|luce|cloud|cultured gray|gray dome)\b", "grey"),
    # Cream / neutral
    (r"\b(cream|crema|beige|biscuit|bone|egyptian stone|cremo delicato)\b", "cream"),
    (r"\b(greige|taupe|tan|taupe fleck|tur)\b", "taupe"),
    # Brown / wood
    (r"\b(brown|marron|teak|wood|walnut|driftwood|castor|corten|iron|bronze)\b", "brown"),
    # Green / blue
    (r"\b(teal|irish green|green|verde|forest|croco)\b", "green"),
    (r"\b(blue|azul|blu|lake blue|bluetta|cobalt)\b", "blue"),
    # Other
    (r"\b(pink|rosa)\b", "pink"),
    (r"\b(red|rosso|orange|arancione)\b", "orange"),
    (r"\b(yellow|giallo|gold|oro|gold granite|goose beak)\b", "yellow"),
    (r"\b(marble)\b", "white"),
    (r"\b(pepper quartz)\b", "grey"),
    (r"\b(cirrus|nix)\b", "grey"),
]

# Keywords that mean dark shade (for grey products) → category "dark"
DARK_KEYWORDS = re.compile(
    r"\b(anthracite|graphite|grafito|carbone|charcoal|galaxy speer|dark grey|"
    r"grigio scuro|noir|black|nero|dark\s*\(?blk\)?)\b",
    re.I
)
# Keywords that mean light shade → category "light"
LIGHT_KEYWORDS = re.compile(
    r"\b(white|bianco|arctic|pure white|ivory|invisible white|snow|ice\s*white|"
    r"sterling|pearl|silver|light grey|luce|cloud|grigio chiaro|calacatta|"
    r"bone|beige|cream|egyptian stone|greige|taupe)\b",
    re.I
)


def get_search_text(entry):
    """Combine name and colour for matching (colour is the actual variant name)."""
    name = (entry.get("name") or "").replace("&quot;", '"').replace("&nbsp;", " ")
    colour = (entry.get("colour") or "").strip()
    if colour and colour not in name:
        return name + " " + colour
    return name


def get_colors(entry):
    text = get_search_text(entry).lower()
    colors = set()
    for pattern, color in COLOR_RULES:
        if re.search(pattern, text, re.I):
            colors.add(color)
    if not colors:
        colors = {"grey"}
    return sorted(colors)


def get_category(entry, colors):
    text = get_search_text(entry).lower()
    colours_set = set(colors)

    # Explicit dark: black or brown
    if {"black", "brown"}.intersection(colours_set):
        return "dark"

    # Dark-grey variants (anthracite, graphite, carbone, etc.)
    if "grey" in colours_set and DARK_KEYWORDS.search(text):
        return "dark"

    # Single white → light
    if colours_set == {"white"}:
        return "light"

    # Single cream, taupe, or white+grey → light
    if colours_set <= {"cream", "taupe"} or colours_set == {"white", "grey"}:
        return "light"

    # Light-grey variants (luce, sterling, pearl, light grey, etc.)
    if colours_set == {"grey"} and LIGHT_KEYWORDS.search(text):
        return "light"

    # Yellow, blue, green often decorative / multicolour
    if len(colours_set) >= 2 or "yellow" in colours_set or "blue" in colours_set or "green" in colours_set:
        return "multicolour"

    # Single grey with no clear light/dark keyword → treat as multicolour (neutral grey)
    if colours_set == {"grey"}:
        return "multicolour"

    return "light"


def main():
    with open(DATA) as f:
        slabs = json.load(f)

    for s in slabs:
        colors = get_colors(s)
        category = get_category(s, colors)
        s["colors"] = colors
        s["category"] = category
        s["product_type"] = "tiles" if s.get("format") == "tile" else "slabs"

    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    print(f"Updated {len(slabs)} porcelain slabs with colors and category.")


if __name__ == "__main__":
    main()
