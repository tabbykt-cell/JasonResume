---
name: site-conventions
description: How jasoncdixon.com is structured and which files must change together. Use when editing any page, résumé fact, contact detail, image, or SEO tag in the JasonResume repo — before making the edit, not after.
---

# jasoncdixon.com — structure and editing rules

A hand-written static site on GitHub Pages. No build step, no framework, no
package manager: the HTML in the repo is byte-for-byte what ships. Edit the
files directly and the change is live on push.

The custom domain lives in `CNAME` (`jasoncdixon.com`). That file is the single
source of truth for the site origin — every absolute URL in the repo must match it.

## Files

| File | What it is |
|---|---|
| `index.html` | Overview page. Sections: About (01), Case studies (02), Experience (03), Colleagues (04), Contact (05) |
| `details.html` | Full detail. Sections: `#journey`, `#capabilities`, `#experience`, `#floor`, `#credentials` |
| `whitepaper.html` | Long-form white paper, gated download |
| `why-implementations-fail.html` | Long-form article with a lead-capture form |
| `llms.txt` | Plain-text summary of the site for AI crawlers. Carries a `Last updated YYYY-MM-DD` line |
| `sitemap.xml` | URLs + per-page image entries with captions. Each `<url>` has a `<lastmod>` |
| `robots.txt` | Crawl rules plus the `Sitemap:` pointer |
| `assets/css/tokens.css` | Design tokens — colors, type scale, spacing. Change here, not in `styles.css` |
| `assets/css/styles.css` | Component styles |
| `assets/img/` | Site imagery (portrait, shop-floor photos) |
| `uploads/` | Downloadables and social images: résumé PDF, OG banners, posters. Most images are paired `.jpeg`/`.webp` |

## The rule that matters: facts live in more than one file

This is where this repo actually breaks. A single fact is duplicated across
pages, and updating one copy silently leaves the rest stale. Before editing any
of these, grep the whole repo for the current value and change **every**
occurrence in the same commit:

- **Email** — `index.html` (JSON-LD, footer, cookie notice), `details.html`,
  `whitepaper.html`, `why-implementations-fail.html`, `llms.txt`
- **Phone** — contact blocks and the résumé PDF
- **LinkedIn handle** — same set, plus JSON-LD `sameAs`
- **Job title / current role / employer** — `index.html` hero and JSON-LD,
  `details.html` experience, `llms.txt` "Current role", and every `og:*` and
  `twitter:*` description that mentions it
- **Domain** — every page's canonical and `og:url`, plus `sitemap.xml`,
  `robots.txt`, `llms.txt`
- **Résumé content** — if the site's work history changes, the PDF at
  `uploads/Jason-C-Dixon-Resume.pdf` is now stale and must be regenerated

Run `python3 plugins/resume-site/scripts/check_site.py` after any such edit;
it detects divergent emails, phones, and LinkedIn handles across files.

## Per-page requirements

Every page needs, and the checker enforces:

- `<link rel="canonical">` matching its own URL at the CNAME origin
  (`index.html` → `https://jasoncdixon.com/`, others → `.../<filename>`)
- `<meta name="description">`
- `og:title`, `og:description`, `og:url` (identical to canonical), `og:image`
- `twitter:card`
- An `alt` on every `<img>` — these are read by recruiters' screen readers and
  by search crawlers, so describe the content, don't restate the filename

## When adding a page

1. Copy the `<head>` block of `details.html` and change canonical, `og:url`,
   title, and descriptions.
2. Add a `<url>` entry to `sitemap.xml` with today's date as `<lastmod>` and
   `<image:image>` entries (with captions) for its significant images.
3. Link it from the site navigation so it is reachable.
4. Mention it in `llms.txt` and bump that file's `Last updated` line.

## When adding an image

- Put site imagery in `assets/img/`, downloadables and social cards in `uploads/`.
- Match the existing `.jpeg` + `.webp` pairing in `uploads/` when the image is
  used on a page, and reference the `.webp` from a `<source>` where the
  surrounding markup already does so.
- Add an `alt`, and add an `<image:image>` entry with a caption to the page's
  `sitemap.xml` block.

## Voice

Plain, concrete, operator-first. Specific numbers over adjectives. No
marketing filler, no em-dash-heavy hype, no "passionate about." Match the tone
already on the page you are editing — read the neighbouring section before
writing new copy.

## Publishing

`main` is what GitHub Pages serves. There is no staging environment, so the
integrity checks are the only gate: run them before pushing. Changes go live
within a minute or so of the push.
