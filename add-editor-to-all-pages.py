#!/usr/bin/env python3
"""
Add visual editor (admin-editor.css + admin-visual-editor.js) to every HTML page
except admin.html. Uses correct relative paths for subdirs (../ or ../../).

Run this script whenever you add NEW HTML pages so the visual editor is available
on every menu page (existing and future):
  python3 scripts/add-editor-to-all-pages.py

Pages that already have the editor are skipped. Any new .html file will get the
editor on first run.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE = {"admin.html"}


def relpath_from_root(filepath):
    return os.path.relpath(filepath, ROOT)


def prefix_for(filepath):
    rel = relpath_from_root(filepath)
    depth = rel.count(os.sep)
    return "../" * depth if depth > 0 else ""


def add_editor_to_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    if "admin-editor.css" in content:
        return False, "already has editor"

    pre = prefix_for(filepath)
    lines = content.split("\n")
    new_lines = []
    css_inserted = False
    script_inserted = False

    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # After first styles.css link, insert admin-editor.css
        if not css_inserted and "styles.css" in line and ("link" in line or "href" in line):
            indent = ""
            if line.strip().startswith("<"):
                indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f'{indent}<link rel="stylesheet" href="{pre}css/admin-editor.css" />')
            css_inserted = True
            i += 1
            continue

        # After any first stylesheet link if no styles.css (e.g. different CSS name)
        if not css_inserted and "<link" in line and "stylesheet" in line and "href=" in line:
            indent = ""
            if line.strip().startswith("<"):
                indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f'{indent}<link rel="stylesheet" href="{pre}css/admin-editor.css" />')
            css_inserted = True
            i += 1
            continue

        # Before first main.js script, insert admin-visual-editor.js
        if not script_inserted and "main.js" in line and "script" in line and "src=" in line:
            indent = ""
            if line.strip().startswith("<"):
                indent = line[: len(line) - len(line.lstrip())]
            new_lines.pop()  # remove current line from new_lines for now
            new_lines.append(f'{indent}<script src="{pre}js/admin-visual-editor.js"></script>')
            new_lines.append(line)
            script_inserted = True
            i += 1
            continue

        # Before any first script src= (for pages without main.js)
        if not script_inserted and "<script" in line and "src=" in line:
            indent = ""
            if line.strip().startswith("<"):
                indent = line[: len(line) - len(line.lstrip())]
            new_lines.pop()
            new_lines.append(f'{indent}<script src="{pre}js/admin-visual-editor.js"></script>')
            new_lines.append(line)
            script_inserted = True
            i += 1
            continue

        i += 1

    if not css_inserted:
        # Fallback: insert before </head>
        for j, ln in enumerate(new_lines):
            if "</head>" in ln:
                indent = ln[: len(ln) - len(ln.lstrip())]
                new_lines.insert(j, f'{indent}<link rel="stylesheet" href="{pre}css/admin-editor.css" />')
                css_inserted = True
                break

    if not script_inserted:
        # Fallback: insert before </body>
        for j, ln in enumerate(new_lines):
            if "</body>" in ln:
                indent = ln[: len(ln) - len(ln.lstrip())]
                new_lines.insert(j, f'{indent}<script src="{pre}js/admin-visual-editor.js"></script>')
                script_inserted = True
                break

    new_content = "\n".join(new_lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True, ("css+script" if css_inserted and script_inserted else "partial")


def main():
    count = 0
    skipped = 0
    for dirpath, _dirnames, filenames in os.walk(ROOT):
        if "node_modules" in dirpath or ".git" in dirpath:
            continue
        for name in filenames:
            if not name.endswith(".html"):
                continue
            if name in EXCLUDE:
                skipped += 1
                continue
            filepath = os.path.join(dirpath, name)
            try:
                ok, msg = add_editor_to_file(filepath)
                if ok:
                    count += 1
                    print(relpath_from_root(filepath), msg)
                else:
                    skipped += 1
            except Exception as e:
                print(relpath_from_root(filepath), "ERROR", e)
    print("Done. Added editor to", count, "files, skipped", skipped)


if __name__ == "__main__":
    main()
