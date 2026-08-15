---
name: site-ship
description: Pre-publish gate — audit, review the diff, then commit and push the résumé site to go live on GitHub Pages.
---

Get pending changes safely onto the live site. `main` is served directly by
GitHub Pages, so this is the only gate between an edit and the public internet.

1. **See what changed:**

   ```bash
   git -C "${CLAUDE_PROJECT_DIR}" status --short && git -C "${CLAUDE_PROJECT_DIR}" diff
   ```

2. **Audit:**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_site.py" --root "${CLAUDE_PROJECT_DIR}"
   ```

   Any error is a stop. Report it and fix it before continuing. Warnings are a
   judgement call — mention them and let the user decide.

3. **Read the diff properly.** Check that:
   - No placeholder or lorem text is going live.
   - No contact detail changed by accident.
   - Copy edits read the way the surrounding page reads.
   - Nothing private or unfinished is in the changeset.

4. **Confirm before publishing.** Summarise what will go live and ask the user
   to confirm. This step publishes to a public site under their own name —
   never skip the confirmation.

5. **Commit and push** on the current branch, with a message describing the
   change in the user's own terms ("Add Q3 case study", not "Update index.html"):

   ```bash
   git -C "${CLAUDE_PROJECT_DIR}" add -A
   git -C "${CLAUDE_PROJECT_DIR}" commit -m "<message>"
   git -C "${CLAUDE_PROJECT_DIR}" push -u origin <current-branch>
   ```

6. Tell the user it takes roughly a minute for Pages to rebuild, and give them
   the URL of what changed.

If the current branch is not `main`, say so — the change will not be live until
that branch reaches `main`.
