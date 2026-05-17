"""Enrich each post page with:

1. Unique <meta name="description"> — first ~160 chars of the body.
2. Article JSON-LD — headline, datePublished, image, author, publisher.
3. BreadcrumbList JSON-LD — Home → Posts (Exposiciones) → Title.

Idempotent: skips pages already marked POST-ENRICHED. Mirrors to both
site/ and public/site/.
"""
import json
import re
from pathlib import Path

REPO = Path("/home/overdrive/claude/enriquetahueso")
ROOTS = [REPO / "site", REPO / "public" / "site"]
SITE_URL = "https://enriquetahueso.com"
OG_IMAGE = f"{SITE_URL}/img/brand/og-image.jpg"
MARKER = "<!-- POST-ENRICHED -->"

MONTHS_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

WHITESPACE = re.compile(r"\s+")


def html_attr_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;")


def parse_spanish_date(text: str) -> str | None:
    """'sábado, 9 de mayo de 2015' → '2015-05-09'."""
    t = text.strip().lower()
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})", t)
    if not m:
        return None
    d = int(m.group(1))
    mon = MONTHS_ES.get(m.group(2))
    if not mon:
        return None
    y = int(m.group(3))
    return f"{y:04d}-{mon:02d}-{d:02d}"


def strip_html(s: str) -> str:
    # Replace common entities
    s = re.sub(r"&nbsp;", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"&amp;", "&", s, flags=re.IGNORECASE)
    s = re.sub(r"&quot;", '"', s, flags=re.IGNORECASE)
    s = re.sub(r"&#39;|&apos;", "'", s, flags=re.IGNORECASE)
    s = re.sub(r"&laquo;", "«", s, flags=re.IGNORECASE)
    s = re.sub(r"&raquo;", "»", s, flags=re.IGNORECASE)
    s = re.sub(r"&[#a-z0-9]+;", "", s, flags=re.IGNORECASE)
    # Drop script/style blocks
    s = re.sub(r"<(script|style)\b.*?</\1>", "", s, flags=re.DOTALL | re.IGNORECASE)
    # Strip all remaining tags
    s = re.sub(r"<[^>]+>", " ", s)
    s = WHITESPACE.sub(" ", s).strip()
    return s


def truncate_for_meta(text: str, limit: int = 160) -> str:
    if len(text) <= limit:
        return text
    # Trim to last word boundary before limit
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.DOTALL | re.IGNORECASE)
POSTDATE_RE = re.compile(
    r'<p[^>]*class="[^"]*post-date[^"]*"[^>]*>(.*?)</p>',
    re.DOTALL | re.IGNORECASE,
)
CONTENT_RE = re.compile(
    r'<div[^>]*class="[^"]*page-content[^"]*"[^>]*>(.*?)<div[^>]*class="[^"]*post-nav',
    re.DOTALL | re.IGNORECASE,
)
# Body starts AFTER the post-date <p>. We capture from end of post-date to
# the post-nav div to get just the post body.
BODY_AFTER_DATE_RE = re.compile(
    r'<p[^>]*class="[^"]*post-date[^"]*"[^>]*>.*?</p>(.*?)<div[^>]*class="[^"]*post-nav',
    re.DOTALL | re.IGNORECASE,
)
FIRST_IMG_RE = re.compile(r'<img[^>]*\bsrc="([^"]+)"', re.IGNORECASE)
DESC_META_RE = re.compile(
    r'<meta\s+name="description"[^>]*>',
    re.IGNORECASE,
)
OG_DESC_RE = re.compile(
    r'(<meta\s+property="og:description"\s+content=")([^"]*)(")',
    re.IGNORECASE,
)
TW_DESC_RE = re.compile(
    r'(<meta\s+name="twitter:description"\s+content=")([^"]*)(")',
    re.IGNORECASE,
)


def canonical_url_for(file_path: Path, root: Path) -> str:
    rel = file_path.relative_to(root).as_posix()
    if rel.endswith(".html"):
        rel = rel[: -len(".html")]
    return f"{SITE_URL}/site/{rel}"


REDO_BLOCK_RE = re.compile(
    rf'\s*{re.escape(MARKER)}\s*<script type="application/ld\+json">.*?</script>\s*',
    re.DOTALL,
)


def enrich(file_path: Path, root: Path, redo: bool = False) -> bool:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    if MARKER in text:
        if not redo:
            return False
        # Strip prior enrichment marker + JSON-LD so we can redo cleanly.
        text = REDO_BLOCK_RE.sub("\n", text)

    # Extract title from H2 (this is the post-specific title in the layout)
    m = H2_RE.search(text)
    if not m:
        return False
    title = strip_html(m.group(1))
    if not title:
        return False

    # Extract date
    pub_date = None
    pm = POSTDATE_RE.search(text)
    if pm:
        date_raw = strip_html(pm.group(1))
        pub_date = parse_spanish_date(date_raw)

    # Extract body text starting AFTER the post-date paragraph so we don't
    # pick up the title/date as the description.
    body = ""
    bm = BODY_AFTER_DATE_RE.search(text)
    if bm:
        body = strip_html(bm.group(1))
    else:
        # Fallback: take from .page-content opening, then drop the title.
        cm = CONTENT_RE.search(text)
        if cm:
            body = strip_html(cm.group(1))
            if body.lower().startswith(title.lower()):
                body = body[len(title):].strip(" .,—-")
    description = truncate_for_meta(body, 160) if body else (
        f"{title} — Galería O+O, Valencia."
    )

    # First image in body for og:image / Article image (fallback to brand og)
    article_img = OG_IMAGE
    im = FIRST_IMG_RE.search(text)
    if im:
        src = im.group(1)
        if src.startswith("http"):
            article_img = src
        elif src.startswith("/"):
            article_img = SITE_URL + src
        else:
            # Relative — posts live at /site/posts/, image src like 'images/x.jpg'
            # or '../images/x.jpg'. Build absolute.
            if src.startswith("../"):
                article_img = f"{SITE_URL}/site/{src[3:]}"
            else:
                article_img = f"{SITE_URL}/site/posts/{src}"

    canonical = canonical_url_for(file_path, root)

    # ----- Build JSON-LD block -----
    article = {
        "@type": "Article",
        "@id": canonical + "#article",
        "headline": title,
        "name": title,
        "description": description,
        "image": article_img,
        "url": canonical,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "inLanguage": "es-ES",
        "author": {
            "@type": "Person",
            "name": "Enriqueta Hueso Martínez",
            "url": SITE_URL + "/",
        },
        "publisher": {
            "@type": "Organization",
            "name": "Galería O+O",
            "logo": {
                "@type": "ImageObject",
                "url": SITE_URL + "/img/brand/favicon-512.png",
            },
        },
    }
    if pub_date:
        article["datePublished"] = pub_date
        article["dateModified"] = pub_date

    breadcrumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio",
             "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Galería O+O",
             "item": SITE_URL + "/site/"},
            {"@type": "ListItem", "position": 3, "name": "Exposiciones",
             "item": SITE_URL + "/site/exposiciones"},
            {"@type": "ListItem", "position": 4, "name": title,
             "item": canonical},
        ],
    }

    graph = {"@context": "https://schema.org", "@graph": [article, breadcrumbs]}
    jsonld = json.dumps(graph, ensure_ascii=False, indent=2)

    # ----- Update meta description (replace existing) -----
    desc_meta = (
        f'<meta name="description" content="{html_attr_escape(description)}">'
    )
    text, _ = DESC_META_RE.subn(desc_meta, text, count=1)

    # Update og:description and twitter:description in place
    text = OG_DESC_RE.sub(
        lambda m: m.group(1) + html_attr_escape(description) + m.group(3), text
    )
    text = TW_DESC_RE.sub(
        lambda m: m.group(1) + html_attr_escape(description) + m.group(3), text
    )

    # Also update og:image to the article image (if we found one)
    text = re.sub(
        r'(<meta\s+property="og:image"\s+content=")[^"]*(")',
        lambda m: m.group(1) + article_img + m.group(2),
        text,
        count=1,
    )
    text = re.sub(
        r'(<meta\s+name="twitter:image"\s+content=")[^"]*(")',
        lambda m: m.group(1) + article_img + m.group(2),
        text,
        count=1,
    )

    # ----- Inject JSON-LD + marker just before </head> -----
    block = (
        f"    {MARKER}\n"
        f'    <script type="application/ld+json">\n{jsonld}\n    </script>\n'
    )
    text = re.sub(r"</head>", block + "</head>", text, count=1, flags=re.IGNORECASE)

    file_path.write_text(text, encoding="utf-8")
    return True


def main():
    import sys
    redo = "--redo" in sys.argv
    enriched = 0
    skipped = 0
    failed = 0
    for root in ROOTS:
        if not root.exists():
            continue
        posts_dir = root / "posts"
        if not posts_dir.exists():
            continue
        for p in sorted(posts_dir.glob("*.html")):
            try:
                if enrich(p, root, redo=redo):
                    enriched += 1
                else:
                    skipped += 1
            except Exception as e:
                failed += 1
                print(f"FAIL {p}: {e}")
    print(f"enriched: {enriched}  skipped: {skipped}  failed: {failed}")


if __name__ == "__main__":
    main()
