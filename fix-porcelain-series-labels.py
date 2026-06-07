#!/usr/bin/env python3
"""
Update porcelain catalogue cards so the short description shows the correct series name.

Example:
  Title:  "Design Industry - Oxyde Dark"
  Before: <p>Porcelain series.</p>
  After:  <p>Design Industry series.</p>

This script only touches entries that currently say "Porcelain series."
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent.parent
HTML_PATH = ROOT / "porcelain-slabs.html"


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")

    # Pattern: capture the series portion before " - " in the title, then the generic description.
    pattern = re.compile(
        r'(<h3><a[^>]*>)([^<]+?)\s*-\s*([^<]+)(</a></h3>\s+)<p>Porcelain series\.</p>',
        re.MULTILINE,
    )

    def repl(match: re.Match) -> str:
        prefix, series, rest, suffix = match.groups()
        series = series.strip()
        return f"{prefix}{series} - {rest}{suffix}<p>{series} series.</p>"

    new_html, count = pattern.subn(repl, html)

    if count:
        HTML_PATH.write_text(new_html, encoding="utf-8")
        print(f"Updated {count} porcelain series labels in {HTML_PATH}")
    else:
        print("No porcelain series labels matched; no changes made.")


if __name__ == "__main__":
    main()

