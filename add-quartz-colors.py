#!/usr/bin/env python3
"""Add color and category metadata to Olympia quartz slabs based on names."""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "olympia-quartz.json"

COLOR_RULES = [
    (r"\b(white|bianco|snow|iceberg|ivory|pearl|harvest)\b", "white"),
    (r"\b(grey|gray|grigio|silver|charcoal)\b", "grey"),
    (r"\b(black|nero|noir)\b", "black"),
    (r"\b(cream|crema|beige|tan)\b", "cream"),
    (r"\b(brown|gold)\b", "brown"),
    (r"\b(green|verde)\b", "green"),
    (r"\b(blue|azul)\b", "blue"),
    (r"\b(pink|rosa)\b", "pink"),
    (r"\b(red|orange)\b", "orange"),
    (r"\b(yellow|golden)\b", "yellow"),
    (r"\b(taupe)\b", "taupe"),
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
    if len(colors_set) >= 3:
        return "multicolour"
    if {"black", "brown"}.intersection(colors_set) or "dark" in name_lower or "nero" in name_lower:
        return "dark"
    if colors_set == {"white"}:
        return "light"
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
    print("Updated", len(slabs), "quartz slabs. Colors used:", sorted(all_colors))


if __name__ == "__main__":
    main()
