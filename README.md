# Jason C. Dixon — Professional Profile Website

Single-page, self-contained site. No build step, no framework, nothing to install.
Everything in this folder is required; nothing else is.

```
index.html      the entire site (HTML, CSS, JS inline)
robots.txt      crawler permissions
sitemap.xml     lists the page + key images for search engines
uploads/        the 8 photos, the video + its poster frame, and the resume PDF
```

**The SEO tags are already set to:** `https://tabbykt-cell.github.io/JasonResume/`

For that address to work, the repository must be **named exactly `JasonResume`**, owned by
**tabbykt-cell**, and set to **Public**. If any of those change, see "Changing the address" below.

---

## 1. Create the repository

1. Signed in as **tabbykt-cell**, go to https://github.com/new
2. Repository name: `JasonResume` (exact spelling and capitalisation — the URL is case-sensitive)
3. Visibility: **Public** (GitHub Pages will not serve a private repo on a free account)
4. Do **not** tick "Add a README" — this folder already has one
5. Click **Create repository**

## 2. Upload the files

1. On the empty repo page, click **uploading an existing file**
2. Open this `github-upload` folder and drag in its **contents** — `index.html`, `robots.txt`,
   `sitemap.xml`, `README.md`, and the `uploads` folder.
   Do **not** drag the `github-upload` folder itself, or every file lands one level too deep
   and the site will 404.
3. Scroll down, click **Commit changes**

## 3. Turn on GitHub Pages

1. In the repo: **Settings → Pages**
2. "Build and deployment" → Source: **Deploy from a branch**
3. Branch: **main**, folder: **/ (root)** → **Save**
4. Wait 1–2 minutes, reload that page, and your site will be live at:

   **https://tabbykt-cell.github.io/JasonResume/**

Check it on your phone too — the layout, the video, and the chat bot all adapt to small screens.

## 4. Tell Google it exists

1. Go to https://search.google.com/search-console
2. Add a property of type **URL prefix**, entering `https://tabbykt-cell.github.io/JasonResume/`
3. Verify ownership using the **HTML tag** method: copy the `<meta name="google-site-verification" ...>`
   tag Google gives you, paste it into `index.html` just below the `<title>` line, commit, then
   click Verify
4. Under **Sitemaps**, submit: `https://tabbykt-cell.github.io/JasonResume/sitemap.xml`
5. Add the site URL to your LinkedIn profile. A link from LinkedIn is the single biggest early
   lever on how fast you start appearing in search results.

### One caveat about robots.txt

Search engines only read `robots.txt` from the root of a domain — in this case
`https://tabbykt-cell.github.io/robots.txt`, which belongs to your account as a whole, not to
this repo. The `robots.txt` here is harmless and correct, but crawlers will not read it at
`/JasonResume/robots.txt`. This costs you nothing: the site is crawlable by default, and
submitting the sitemap directly in Search Console (step 4) does the real work.

If you ever want control of that root file, create a second repo named exactly
`tabbykt-cell.github.io` — that one publishes at the domain root.

---

## Changing the address later

If you rename the repo, change accounts, or buy a real domain, find and replace

    https://tabbykt-cell.github.io/JasonResume

with the new address in **three files**: `index.html` (canonical tag, Open Graph tags, Twitter
tags, and the structured-data block near the top), `sitemap.xml`, and `robots.txt`.

This matters more than it looks. Those tags tell Google which address is the authoritative copy
of the page. If they point somewhere that is not your live site, Google may show that address
instead of yours — or show nothing at all.

For a custom domain: add it under **Settings → Pages → Custom domain**, tick **Enforce HTTPS**,
add the DNS records GitHub shows you at your registrar, then do the find-and-replace above.

---

## Editing the site later

Everything is in `index.html`. Landmarks if you open it in a text editor:

- **SEO tags** — the top ~90 lines
- **"Ask about Jason" bot** — search for `var KB = [`. Each entry has `k` (words that trigger it)
  and `a` (the answer). Edit `a` to reword an answer; copy an entry to add a new topic. There is
  no AI model and no API key behind it, so it can only ever say what is written there — which is
  also why it cannot invent anything about you.
- **Video** — search for `aboutVid`. Silent and looping by design; the audio track was removed
  from the file itself.
- **Resume** — drop a new PDF at `uploads/Jason-C-Dixon-Resume.pdf` (same filename) and both
  download buttons keep working.

This README is documentation only — not part of the website. Delete it if you prefer a repo
containing nothing but the site.
