---
name: site-check
description: Audit the résumé site for broken links, missing assets, SEO metadata problems, sitemap drift, and inconsistent contact details.
---

Run a full integrity audit of the site.

1. Run the checker:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_site.py" --root "${CLAUDE_PROJECT_DIR}"
   ```

2. Report the results grouped by severity, with the file and what to change.
   Errors are things that are wrong on the live site — dead references,
   contradictory contact details, a canonical URL pointing at the wrong page.
   Warnings are gaps worth closing but not breakage.

3. For each finding, say what the fix is. Do not apply fixes unless the user
   asks — this command reports.

If `$ARGUMENTS` names specific files, pass them via `--files` to scope the
page-level checks to those files.

The checker only sees what it can verify statically. Also skim for things it
cannot catch and mention anything you spot: prose that contradicts itself
between `index.html` and `details.html`, a `llms.txt` summary that no longer
matches the pages it describes, or a stale `Last updated` date.
