#!/usr/bin/env python3
"""Add color and category metadata to Olympia granite slabs based on names."""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-granite.json"

COLOR_RULES = [
    (r"\b(white|bianco|blanco|snow|iceberg|ivory|pearl)\b", "white"),
    (r"\b(grey|gray|grigio|gris|silver|charcoal)\b", "grey"),
    (r"\b(black|nero|noir|negro)\b", "black"),
    (r"\b(cream|crema|beige|tan|biscuit|cappucino)\b", "cream"),
    (r"\b(brown|marron|marrone|teak|wood|walnut)\b", "brown"),
    (r"\b(green|verde|forest|irish)\b", "green"),
    (r"\b(blue|azul|blu|savoie)\b", "blue"),
    (r"\b(pink|rosa)\b", "pink"),
    (r"\b(red|rosso|rojo|orange|arancione)\b", "orange"),
    (r"\b(yellow|giallo|gold|oro|golden)\b", "yellow"),
    (r"\b(taupe)\b", "taupe"),
    (r"\b(purple|violet|lavender)\b", "purple"),
]


def get_colors(name):
    name_lower = name.lower()
    colors = set()
    for pattern, color in COLOR_RULES:
        if re.search(pattern, name_lower, re.I):
            colors.add(color)
    if not colors:
        colors = {"grey"}
    return sorted(colors)


def get_category(name, colors):
    name_lower = name.lower()
    colors_set = set(colors)
    if "multicolour" in colors_set or len(colors_set) >= 3:
        return "multicolour"
    if {"black", "brown"}.intersection(colors_set) or "dark" in name_lower or "noir" in name_lower or "nero" in name_lower:
        return "dark"
    if "orange" in colors_set:
        return "multicolour"
    if colors_set == {"white"}:
        return "light"
    if colors_set == {"grey"}:
        return "light" if any(x in name_lower for x in ["silver", "pearl", "snow", "light"]) else "multicolour"
    if colors_set <= {"white", "grey"}:
        return "light"
    return "multicolour"


def main():
    with open(DATA) as f:
        slabs = json.load(f)

    for s in slabs:
        name = s.get("name", "").replace("&quot;", '"').replace("&nbsp;", " ")
        colors = get_colors(name)
        category = get_category(name, colors)
        s["colors"] = colors
        s["category"] = category

    with open(DATA, "w") as f:
        json.dump(slabs, f, indent=2)

    all_colors = set()
    for s in slabs:
        all_colors.update(s.get("colors", []))
    print(f"Updated {len(slabs)} granite slabs. Colors used: {sorted(all_colors)}")


if __name__ == "__main__":
    main()
