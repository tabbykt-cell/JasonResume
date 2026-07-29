# Jason C. Dixon — Professional Profile Website

Single-page, self-contained site, live at **https://jasoncdixon.com/**.
No build step, no framework, nothing to install. Hosted on GitHub Pages from this repo.

```
index.html      the entire site (HTML, CSS, JS inline)
CNAME           holds the custom domain (jasoncdixon.com) for GitHub Pages
favicon.ico     browser-tab and Google-results icon (16/32/48px)
apple-touch-icon.png  iOS home-screen icon (180px)
robots.txt      crawler permissions (search + AI) + sitemap pointer
sitemap.xml     lists the page + key images for search engines
llms.txt        plain-text summary of the site for AI assistants
uploads/        photos (JPEG + WebP pairs), the video + poster frames,
                the share banner (og-banner-v2.jpg), and the resume PDF
```

## Hosting

GitHub Pages serves the `main` branch root (**Settings → Pages**). The custom
domain is set there and mirrored in the `CNAME` file — if that file is ever
deleted, Pages drops back to the github.io address and the DNS setup breaks.
**Enforce HTTPS** should stay ticked.

Because the site lives at the domain root, `robots.txt` and `sitemap.xml` are
served from `https://jasoncdixon.com/` and work exactly as search engines expect.

## Changing the address later

If the domain ever changes, find and replace `https://jasoncdixon.com` in
**three files**: `index.html` (canonical tag, Open Graph/Twitter tags, and both
structured-data blocks near the top), `sitemap.xml`, and `robots.txt` — then
update the Pages custom-domain setting and the `CNAME` file.

Those tags tell Google which address is the authoritative copy of the page. If
they point somewhere that is not the live site, Google may show that address
instead — or nothing at all.

## Things wired into the page

- **Contact form** — the "Get in touch" / email links open a modal that submits
  to [Web3Forms](https://web3forms.com) and lands in Jason's inbox. The access
  key sits in the hidden `access_key` input inside `index.html` (search for
  `cfForm`). Web3Forms access keys are public by design; to rotate one, generate
  a new key on web3forms.com and paste it there.
- **Google Analytics + cookie banner** — not active yet. Search `index.html` for
  `GA_ID` and replace the `G-XXXXXXXXXX` placeholder with a real GA4 Measurement
  ID. Until then the consent banner stays hidden and no analytics load; once a
  real ID is in place, the banner appears and GA loads only after a visitor
  accepts.
- **"Ask about Jason" bot** — search for `var KB = [`. Each entry has `k` (words
  that trigger it) and `a` (the answer). Edit `a` to reword an answer; copy an
  entry to add a new topic. There is no AI model behind it, so it can only ever
  say what is written there.
- **Video** — search for `aboutVid`. Silent and looping by design; the audio
  track was removed from the file itself.
- **Resume** — drop a new PDF at `uploads/Jason-C-Dixon-Resume.pdf` (same
  filename) and both download buttons keep working.

## Search Console

The site is verified in Google Search Console (the `google-site-verification`
meta tag near the top of `index.html`). If you edit content meaningfully, update
`<lastmod>` in `sitemap.xml` — it is maintained by hand.

## Being readable by AI assistants

The site is set up so that when someone asks ChatGPT, Claude, Perplexity, or
Google about Jason, the assistant can find and quote it accurately:

- **`robots.txt`** explicitly allows every major search and AI crawler. Some AI
  crawlers check for their own user-agent before falling back to `*`, so they
  are named individually.
- **JSON-LD structured data** in `index.html` states the facts in the format
  machines parse most reliably: a `Person` record (job title, employer,
  location, email, LinkedIn, education, and 39 `knowsAbout` skill terms),
  `WebSite`, `ProfilePage`, and a 34-question `FAQPage`.
- **`llms.txt`** is a plain-language summary of the whole profile at the domain
  root, a convention some AI tools look for.
- The page is **static HTML** — all text is in the file that gets served, not
  assembled by JavaScript, so any crawler that fetches the URL gets everything.

**Keeping them in sync:** the FAQ block and `llms.txt` are both derived from the
ask-bot's `var KB = [` array in `index.html`. If you change a fact, change it in
the KB, then mirror it into the FAQ JSON-LD and `llms.txt` so the three do not
drift apart. Update the date at the top of `llms.txt` when you do.

## Icons

`favicon.ico` and `apple-touch-icon.png` sit at the repo root, where browsers
and crawlers look for them by default, and are also declared with `<link>` tags
in `index.html` alongside the inline SVG icon (which modern browsers prefer for
tabs). All three use the same mark: a blue square, a cream square, dark
background. To change the artwork, replace both files at the same sizes
(16/32/48 px in the .ico, 180×180 for the PNG) and update the inline SVG.

This README is documentation only — not part of the website.
