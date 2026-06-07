# Visual editor on every page

The visual admin editor (edit mode with ?edit=1) is included on **every HTML page** except `admin.html`.

## Existing pages

All current menu and content pages already include:

- `css/admin-editor.css`
- `js/admin-visual-editor.js`

(with correct relative paths for subfolders).

## Future pages

When you **add new HTML pages** (new menu items, new blog posts, new material pages, etc.):

1. Run the script once to add the editor to any new files:

   ```bash
   python3 scripts/add-editor-to-all-pages.py
   ```

2. The script skips pages that already have the editor and only updates new or modified HTML files that are missing it.

So every existing and future menu page will have the visual editor (Format text, Replace logo, Edit menu/submenu, Add section, etc.) when you open it with `?edit=1` after logging in at `admin.html`.
