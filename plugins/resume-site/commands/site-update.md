---
name: site-update
description: Change a fact on the résumé site (contact detail, role, dates, copy) and propagate it to every file that carries it.
---

Update site content described by `$ARGUMENTS`, making sure the change lands
everywhere the fact appears rather than in the one file that came to mind first.

Follow the `site-conventions` skill for which files carry which facts.

**Method:**

1. **Find every copy first.** Grep the repo for the *current* value before
   changing anything — the old email, the old title, the old date. Include
   `.html`, `llms.txt`, `sitemap.xml`, and `robots.txt`. List what you found
   and where.

2. **Check the structured data too.** `index.html` carries a JSON-LD block with
   the same facts as the visible page. It is easy to miss and it is what Google
   reads. Also check `og:*` and `twitter:*` descriptions, which often restate
   the role or tagline.

3. **Make the edits in one pass**, matching each file's existing tone and markup.

4. **Update the dependent metadata:**
   - Touched a page's substance → bump its `<lastmod>` in `sitemap.xml` to today.
   - Touched anything `llms.txt` describes → update that text and its
     `Last updated` line.
   - Changed résumé substance (roles, dates, responsibilities) → tell the user
     the PDF at `uploads/Jason-C-Dixon-Resume.pdf` is now stale, since it cannot
     be regenerated from the HTML automatically.

5. **Verify:**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_site.py" --root "${CLAUDE_PROJECT_DIR}"
   ```

6. Summarise every file you changed and anything left for the user to do by
   hand.

If the request is ambiguous about scope — say, a title change that may or may
not apply to the white paper byline — ask before guessing.
