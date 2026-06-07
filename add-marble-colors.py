#!/usr/bin/env python3
"""Add color and category metadata to Olympia marble slabs based on names."""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-marble.json"

# Color keywords -> filter value (lowercase)
COLOR_RULES = [
    (r"\b(white|bianco|blanco|perlato|calacatta|statuario|thassos|sivec|invisible|alabaster|alabastro|snow|neve|iceberg|ivory)\b", "white"),
    (r"\b(grey|gray|grigio|gris|grey|silver)\b", "grey"),
    (r"\b(black|nero|noir|negro)\b", "black"),
    (r"\b(cream|crema|beige|botticino|biscuit|cappucino)\b", "cream"),
    (r"\b(brown|marron|marrone|emperador|teak|wood|walnut)\b", "brown"),
    (r"\b(green|verde|forest|irish)\b", "green"),
    (r"\b(blue|azul|blu|savoie|savoia)\b", "blue"),
    (r"\b(pink|rosa|aurora)\b", "pink"),
    (r"\b(red|rosso|rojo|alicante|orange|arancione)\b", "orange"),
    (r"\b(yellow|giallo|gold|oro|golden)\b", "yellow"),
    (r"\b(taupe|tan)\b", "taupe"),
    (r"\b(purple|violet|lavender)\b", "purple"),
]

def get_colors(name):
    """Extract color tags from slab name."""
    name_lower = name.lower()
    colors = set()
    for pattern, color in COLOR_RULES:
        if re.search(pattern, name_lower, re.I):
            colors.add(color)
    # Fallbacks for common names
    if not colors:
        if "arabescato" in name_lower or "breccia" in name_lower:
            colors = {"white", "grey"}  # typically white with grey veins
        elif "zebrino" in name_lower:
            colors = {"white", "grey"} if "negro" in name_lower else {"white", "grey"}
        elif "calacatta" in name_lower or "carrara" in name_lower:
            colors = {"white", "grey"}
        elif "port" in name_lower and "black" in name_lower:
            colors = {"black"}
        elif "fossil" in name_lower:
            colors = {"brown", "grey"}
        elif "rain forest" in name_lower:
            colors = {"green", "brown"}
        elif "arco iris" in name_lower:
            colors = {"multicolour"}
        elif "aqua" in name_lower or "marina" in name_lower:
            colors = {"blue", "green"}
    if not colors:
        colors = {"grey"}  # default
    return sorted(colors)

def get_category(name, colors):
    """light = whites or very light greys only; dark; multicolour = everything else."""
    name_lower = name.lower()
    colors_set = set(colors)
    if "multicolour" in colors_set or len(colors_set) >= 3:
        return "multicolour"
    dark_indicators = "dark" in name_lower or "noir" in name_lower or "nero" in name_lower
    if {"black", "brown"}.intersection(colors_set) or dark_indicators:
        return "dark"
    if "orange" in colors_set:
        return "multicolour"
    # Light = white only, or very light grey (silver, pearl, ice, sivec, etc.)
    if colors_set == {"white"}:
        return "light"
    if colors_set == {"grey"}:
        very_light_grey = any(x in name_lower for x in [
            "silver", "pearl", "ice", "sivec", "snow", "neve", "light", "athena",
            "iceberg", "frozen", "invisible", "gala"
        ])
        return "light" if very_light_grey else "multicolour"
    if "white" in colors_set and colors_set <= {"white", "grey"}:
        # White + grey veins (e.g. Carrara, Calacatta) -> light
        return "light"
    # Cream, taupe, yellow, pink, blue, green, etc. -> multicolour
    return "multicolour"

def main():
    with open(DATA) as f:
        slabs = json.load(f)

    all_colors = set()
    for s in slabs:
        name = s.get("name", "").replace("&quot;", '"').replace("&nbsp;", " ")
        colors = get_colors(name)
        if s.get("format") == "tile":
            category = "tiles"
        else:
            category = get_category(name, colors)
        s["colors"] = colors
        s["category"] = category
        all_colors.update(colors)

    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    print(f"Updated {len(slabs)} slabs. Colors used: {sorted(all_colors)}")

if __name__ == "__main__":
    main()
