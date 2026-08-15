#!/usr/bin/env python3
"""Integrity checks for the jasoncdixon.com static site.

Catches the failure modes this repo actually hits: a fact updated on one page
but not the other five, a renamed asset that leaves a dead reference, an SEO
tag that drifts away from the canonical URL.

Dependency-free (stdlib only). Run from anywhere:

    python3 scripts/check_site.py                 # full audit
    python3 scripts/check_site.py --files index.html
    python3 scripts/check_site.py --errors-only

Exit status: 0 clean, 1 errors found.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
              "image": "http://www.google.com/schemas/sitemap-image/1.1"}

# Pages that are standalone lead-gen/long-form pieces rather than core profile
# pages. They are held to the same link/asset standard but are not required to
# appear in the sitemap.
SITEMAP_OPTIONAL = {"whitepaper.html"}

REQUIRED_META = ["description"]
REQUIRED_OG = ["og:title", "og:description", "og:url", "og:image"]

ERROR, WARN = "ERROR", "WARN"


@dataclass
class Finding:
    level: str
    where: str
    message: str

    def __str__(self) -> str:
        tag = "\033[31mERROR\033[0m" if self.level == ERROR else "\033[33mWARN \033[0m"
        if not sys.stdout.isatty():
            tag = self.level.ljust(5)
        return f"  {tag}  {self.where}: {self.message}"


@dataclass
class Page:
    path: Path
    name: str
    links: list = field(default_factory=list)   # (attr_value, tag)
    images: list = field(default_factory=list)  # (src, alt_or_None)
    metas: dict = field(default_factory=dict)   # name/property -> content
    canonical: str = ""
    ids: set = field(default_factory=set)
    anchors: list = field(default_factory=list)
    text: str = ""


class PageParser(HTMLParser):
    """Collects the handful of things the checks care about."""

    def __init__(self, page: Page):
        super().__init__(convert_charrefs=True)
        self.page = page

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        p = self.page

        if "id" in a and a["id"]:
            p.ids.add(a["id"])

        if tag == "a" and a.get("href"):
            href = a["href"]
            if href.startswith("#"):
                p.anchors.append(href[1:])
            else:
                p.links.append((href, "a"))

        elif tag == "img":
            src = a.get("src", "")
            if src:
                p.links.append((src, "img"))
            p.images.append((src or "(no src)", a.get("alt")))

        elif tag == "source" and a.get("srcset"):
            for candidate in a["srcset"].split(","):
                url = candidate.strip().split(" ")[0]
                if url:
                    p.links.append((url, "source"))

        elif tag in ("script", "video") and a.get("src"):
            p.links.append((a["src"], tag))

        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            href = a.get("href", "")
            if "canonical" in rel:
                p.canonical = href
            elif href and rel not in ("dns-prefetch", "preconnect"):
                p.links.append((href, "link"))

        elif tag == "meta":
            key = a.get("property") or a.get("name")
            if key:
                p.metas[key.lower()] = a.get("content", "")

    def handle_data(self, data):
        self.page.text += data


def load_pages(root: Path, only: list[str] | None) -> list[Page]:
    names = sorted(p.name for p in root.glob("*.html"))
    if only:
        wanted = {Path(f).name for f in only}
        names = [n for n in names if n in wanted]
    pages = []
    for name in names:
        path = root / name
        page = Page(path=path, name=name)
        PageParser(page).feed(path.read_text(encoding="utf-8", errors="replace"))
        pages.append(page)
    return pages


def site_origin(root: Path) -> str:
    cname = root / "CNAME"
    if cname.exists():
        domain = cname.read_text(encoding="utf-8").strip()
        if domain:
            return f"https://{domain}"
    return ""


def local_target(url: str, origin: str) -> str | None:
    """Map a URL to a repo-relative path, or None if it is external/not a file."""
    url = url.strip()
    if not url or url.startswith(("mailto:", "tel:", "data:", "javascript:", "#")):
        return None
    if origin and url.startswith(origin):
        url = url[len(origin):] or "/"
    elif re.match(r"^[a-z]+://", url) or url.startswith("//"):
        return None
    url = url.split("#")[0].split("?")[0]
    if not url:
        return None
    if url.endswith("/"):
        url += "index.html"
    return url.lstrip("/")


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_links(root: Path, pages: list[Page], origin: str) -> list[Finding]:
    out = []
    for page in pages:
        for url, tag in page.links:
            target = local_target(url, origin)
            if target and not (root / target).exists():
                out.append(Finding(ERROR, page.name, f"<{tag}> references missing file: {url}"))
    return out


def check_anchors(pages: list[Page]) -> list[Finding]:
    out = []
    for page in pages:
        for anchor in page.anchors:
            if anchor and anchor not in page.ids:
                out.append(Finding(WARN, page.name, f'link to "#{anchor}" but no element has that id'))
    return out


def check_alt_text(pages: list[Page]) -> list[Finding]:
    out = []
    for page in pages:
        for src, alt in page.images:
            if alt is None:
                out.append(Finding(ERROR, page.name, f"<img> has no alt attribute: {src}"))
            elif not alt.strip():
                out.append(Finding(WARN, page.name, f"<img> has empty alt (decorative?): {src}"))
    return out


def check_seo(pages: list[Page], origin: str) -> list[Finding]:
    out = []
    for page in pages:
        expected = f"{origin}/" if page.name == "index.html" else f"{origin}/{page.name}"

        if not page.canonical:
            out.append(Finding(ERROR, page.name, "no <link rel=\"canonical\"> tag"))
        elif origin and page.canonical.rstrip("/") != expected.rstrip("/"):
            out.append(Finding(ERROR, page.name,
                               f"canonical is {page.canonical!r}, expected {expected!r}"))

        for name in REQUIRED_META:
            if not page.metas.get(name, "").strip():
                out.append(Finding(WARN, page.name, f'missing <meta name="{name}">'))

        for prop in REQUIRED_OG:
            if not page.metas.get(prop, "").strip():
                out.append(Finding(WARN, page.name, f'missing <meta property="{prop}">'))

        og_url = page.metas.get("og:url", "")
        if og_url and page.canonical and og_url.rstrip("/") != page.canonical.rstrip("/"):
            out.append(Finding(ERROR, page.name,
                               f"og:url ({og_url}) does not match canonical ({page.canonical})"))

        if not page.metas.get("twitter:card", "").strip():
            out.append(Finding(WARN, page.name, 'missing <meta name="twitter:card">'))
    return out


def check_origin_drift(root: Path, pages: list[Page], origin: str) -> list[Finding]:
    """Absolute self-links must use the domain in CNAME."""
    out = []
    if not origin:
        return out
    host = origin.split("//")[1]
    stale = re.compile(r"https?://([a-z0-9-]+\.github\.io|www\." + re.escape(host) + r")\S*")
    for path in list(pages and [p.path for p in pages] or []) + [root / "sitemap.xml",
                                                                root / "robots.txt",
                                                                root / "llms.txt"]:
        if not path.exists():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for match in stale.findall(line):
                out.append(Finding(WARN, f"{path.name}:{i}",
                                   f"URL uses {match} — CNAME says the site is {host}"))
    return out


def check_sitemap(root: Path, pages: list[Page], origin: str, full: bool) -> list[Finding]:
    out = []
    sitemap = root / "sitemap.xml"
    if not sitemap.exists():
        return [Finding(ERROR, "sitemap.xml", "file is missing")]

    try:
        tree = ET.parse(sitemap)
    except ET.ParseError as exc:
        return [Finding(ERROR, "sitemap.xml", f"is not valid XML: {exc}")]

    listed = set()
    for url_el in tree.getroot().findall("sm:url", SITEMAP_NS):
        loc_el = url_el.find("sm:loc", SITEMAP_NS)
        if loc_el is None or not (loc_el.text or "").strip():
            out.append(Finding(ERROR, "sitemap.xml", "a <url> entry has no <loc>"))
            continue
        loc = loc_el.text.strip()

        target = local_target(loc, origin)
        if target:
            listed.add(target)
            if not (root / target).exists():
                out.append(Finding(ERROR, "sitemap.xml", f"lists a URL with no file behind it: {loc}"))

        lastmod_el = url_el.find("sm:lastmod", SITEMAP_NS)
        if lastmod_el is None or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", (lastmod_el.text or "").strip()):
            out.append(Finding(WARN, "sitemap.xml", f"{loc} has a missing or malformed <lastmod>"))

        for img in url_el.findall("image:image", SITEMAP_NS):
            img_loc = img.find("image:loc", SITEMAP_NS)
            if img_loc is None or not (img_loc.text or "").strip():
                continue
            img_target = local_target(img_loc.text.strip(), origin)
            if img_target and not (root / img_target).exists():
                out.append(Finding(ERROR, "sitemap.xml",
                                   f"image entry points at a missing file: {img_loc.text.strip()}"))

    if full:
        for page in pages:
            if page.name in SITEMAP_OPTIONAL:
                continue
            if page.name not in listed:
                out.append(Finding(WARN, "sitemap.xml", f"{page.name} is not listed"))
    return out


def check_robots(root: Path, origin: str) -> list[Finding]:
    robots = root / "robots.txt"
    if not robots.exists():
        return [Finding(WARN, "robots.txt", "file is missing")]
    body = robots.read_text(encoding="utf-8", errors="replace")
    out = []
    if "Sitemap:" not in body:
        out.append(Finding(WARN, "robots.txt", "has no Sitemap: line"))
    elif origin and f"{origin}/sitemap.xml" not in body:
        out.append(Finding(WARN, "robots.txt", f"Sitemap: line does not point at {origin}/sitemap.xml"))
    return out


def check_llms_txt(root: Path, origin: str) -> list[Finding]:
    llms = root / "llms.txt"
    if not llms.exists():
        return [Finding(WARN, "llms.txt", "file is missing")]
    body = llms.read_text(encoding="utf-8", errors="replace")
    out = []
    if not re.search(r"[Ll]ast updated\s+\d{4}-\d{2}-\d{2}", body):
        out.append(Finding(WARN, "llms.txt", 'no "Last updated YYYY-MM-DD" line'))
    for url in set(re.findall(r"https?://\S+", body)):
        url = url.rstrip(".,)")
        target = local_target(url, origin)
        if target and not (root / target).exists():
            out.append(Finding(ERROR, "llms.txt", f"links to a missing file: {url}"))
    return out


def check_contact_consistency(root: Path, origin: str) -> list[Finding]:
    """The whole point: one fact, many files, no drift."""
    out = []
    files = sorted(root.glob("*.html")) + [root / "llms.txt"]
    files = [f for f in files if f.exists()]

    emails: dict[str, list[str]] = {}
    linkedins: dict[str, list[str]] = {}
    for path in files:
        body = path.read_text(encoding="utf-8", errors="replace")
        # Skip form placeholders — they are sample text, not contact details.
        body = re.sub(r'placeholder="[^"]*"', "", body)
        for email in set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", body)):
            if email.endswith((".png", ".jpg", ".svg")):
                continue
            emails.setdefault(email.lower(), []).append(path.name)
        for handle in set(re.findall(r"linkedin\.com/in/([\w-]+)", body, re.I)):
            linkedins.setdefault(handle.lower(), []).append(path.name)

    real = {e: f for e, f in emails.items() if "example.com" not in e and "company.com" not in e}
    if len(real) > 1:
        detail = "; ".join(f"{e} in {', '.join(sorted(set(f)))}" for e, f in sorted(real.items()))
        out.append(Finding(ERROR, "contact", f"more than one email address in use — {detail}"))

    if len(linkedins) > 1:
        detail = "; ".join(f"/in/{h} in {', '.join(sorted(set(f)))}" for h, f in sorted(linkedins.items()))
        out.append(Finding(ERROR, "contact", f"more than one LinkedIn handle in use — {detail}"))

    # Phone numbers, if present anywhere, should be present consistently.
    phone_re = re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}")
    phones: dict[str, list[str]] = {}
    for path in files:
        body = re.sub(r'placeholder="[^"]*"', "",
                      path.read_text(encoding="utf-8", errors="replace"))
        for raw in set(phone_re.findall(body)):
            digits = re.sub(r"\D", "", raw)
            if digits.startswith("555"):
                continue
            phones.setdefault(digits, []).append(path.name)
    if len(phones) > 1:
        detail = "; ".join(f"{d} in {', '.join(sorted(set(f)))}" for d, f in sorted(phones.items()))
        out.append(Finding(ERROR, "contact", f"more than one phone number in use — {detail}"))
    return out


def check_resume_pdf(root: Path) -> list[Finding]:
    pdf = root / "uploads" / "Jason-C-Dixon-Resume.pdf"
    if not pdf.exists():
        return [Finding(WARN, "uploads/", "Jason-C-Dixon-Resume.pdf is missing")]
    index = root / "index.html"
    details = root / "details.html"
    newest = max((f.stat().st_mtime for f in (index, details) if f.exists()), default=0)
    if newest > pdf.stat().st_mtime:
        return [Finding(WARN, "uploads/Jason-C-Dixon-Resume.pdf",
                        "site pages are newer than the PDF — regenerate it if the résumé content changed")]
    return []


# --------------------------------------------------------------------------

def run(root: Path, only: list[str] | None) -> list[Finding]:
    origin = site_origin(root)
    pages = load_pages(root, only)
    full = not only

    findings = []
    findings += check_links(root, pages, origin)
    findings += check_anchors(pages)
    findings += check_alt_text(pages)
    findings += check_seo(pages, origin)
    findings += check_origin_drift(root, pages, origin)
    if full:
        findings += check_sitemap(root, pages, origin, full)
        findings += check_robots(root, origin)
        findings += check_llms_txt(root, origin)
        findings += check_contact_consistency(root, origin)
        findings += check_resume_pdf(root)
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Integrity checks for the résumé site.")
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR", "."),
                    help="repo root (default: CLAUDE_PROJECT_DIR or cwd)")
    ap.add_argument("--files", nargs="*", help="limit page checks to these HTML files")
    ap.add_argument("--errors-only", action="store_true", help="suppress warnings")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not (root / "index.html").exists():
        print(f"check_site: no index.html under {root} — is --root correct?", file=sys.stderr)
        return 1

    findings = run(root, args.files)
    errors = [f for f in findings if f.level == ERROR]
    warns = [f for f in findings if f.level == WARN]
    shown = errors if args.errors_only else findings

    scope = ", ".join(args.files) if args.files else "whole site"
    if shown:
        print(f"Site check ({scope}):")
        for finding in shown:
            print(finding)
    if shown:
        hidden = " (warnings hidden)" if args.errors_only and warns else ""
        print(f"\n{len(errors)} error(s), {len(warns)} warning(s).{hidden}")
    else:
        print(f"Site check ({scope}): clean.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
