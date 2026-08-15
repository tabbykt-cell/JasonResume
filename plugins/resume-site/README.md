# Résumé Site Toolkit

A Claude Code plugin for maintaining [jasoncdixon.com](https://jasoncdixon.com).

The site is hand-written static HTML served by GitHub Pages, with no build step
and no staging environment — a push is a publish. The same facts (email, phone,
job title, domain) are duplicated across five or six files, so the usual failure
is updating one copy and leaving the rest stale. This plugin closes that gap.

## Install

From the repo root:

```
/plugin marketplace add tabbykt-cell/JasonResume
/plugin install resume-site@jasoncdixon
```

For local development, point the marketplace at the working copy instead:

```
/plugin marketplace add ./
```

## What you get

**Commands**

| Command | What it does |
|---|---|
| `/resume-site:site-check` | Full audit — broken references, SEO metadata, sitemap drift, contact-detail conflicts |
| `/resume-site:site-update` | Make a content change and propagate it to every file that carries the same fact |
| `/resume-site:site-ship` | Pre-publish gate: audit, review the diff, confirm, commit, push |

**Skill** — `site-conventions` loads automatically when editing the site. It
documents which file holds what, which facts are duplicated where, the required
metadata for every page, and the steps for adding a page or an image.

**Agent** — `site-auditor` is a read-only reviewer for the things a script
cannot check: factual contradictions between pages, stale `llms.txt` copy, tone
drift, and alt text that is present but useless.

**Hook** — after any `Write` or `Edit` to a top-level `.html`, `.xml`, or `.txt`
file, the integrity checks run against that file. Errors are surfaced
immediately so they get fixed in the same turn. Warnings and clean runs stay
silent.

## The checker

`scripts/check_site.py` is plain Python 3, stdlib only, and runs standalone:

```bash
python3 plugins/resume-site/scripts/check_site.py            # full audit
python3 plugins/resume-site/scripts/check_site.py --files index.html
python3 plugins/resume-site/scripts/check_site.py --errors-only
```

Exit status is 1 when there are errors, so it drops into CI or a pre-commit
hook unchanged.

It verifies:

- every local `href`/`src`/`srcset` target exists on disk
- every `#anchor` has a matching `id` on the same page
- every `<img>` has an `alt`
- each page has a canonical URL matching its own address at the `CNAME` origin,
  plus `description`, the four core `og:*` tags, and `twitter:card`
- `og:url` agrees with the canonical
- no absolute URL still points at `*.github.io` or a `www.` variant after a
  domain change
- `sitemap.xml` parses, every `<loc>` and `<image:loc>` resolves to a real file,
  every entry has a well-formed `<lastmod>`, and no page is missing
- `robots.txt` points at the real sitemap
- `llms.txt` has a `Last updated` date and no dead links
- email, phone, and LinkedIn handle are identical everywhere they appear
  (form placeholders and `555` numbers excluded)
- the résumé PDF is not older than the pages it mirrors

## Adapting it

The structure is generic even though the checks are not. `check_site.py` reads
the origin from `CNAME` and discovers pages by globbing `*.html`, so it works on
any flat static site. To retarget it, adjust `SITEMAP_OPTIONAL`, the required
metadata lists at the top of the file, and the paths named in
`check_resume_pdf`.
