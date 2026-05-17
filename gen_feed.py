"""Generate an Atom feed (feed.xml) from the legacy posts.

Atom 1.0 — more modern and well-supported than RSS 2.0; many readers
(Feedly, Inoreader, NetNewsWire) parse it natively. Google Discover
also picks up feeds.
"""
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

REPO = Path("/home/overdrive/claude/enriquetahueso")
PUBLIC = REPO / "public"
POSTS_DIR = PUBLIC / "site" / "posts"
SITE_URL = "https://enriquetahueso.com"
FEED_URL = SITE_URL + "/feed.xml"
MAX_ENTRIES = 40

MONTHS_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.DOTALL | re.IGNORECASE)
POSTDATE_RE = re.compile(
    r'<p[^>]*class="[^"]*post-date[^"]*"[^>]*>(.*?)</p>',
    re.DOTALL | re.IGNORECASE,
)
DESC_META_RE = re.compile(
    r'<meta\s+name="description"\s+content="([^"]*)"', re.IGNORECASE
)
WHITESPACE = re.compile(r"\s+")


def strip(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return WHITESPACE.sub(" ", unescape(s)).strip()


def parse_spanish_date(text: str):
    t = strip(text).lower()
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})", t)
    if not m:
        return None
    d, mon, y = int(m.group(1)), MONTHS_ES.get(m.group(2)), int(m.group(3))
    if not mon:
        return None
    return datetime(y, mon, d, 12, 0, tzinfo=timezone.utc)


def xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def collect_posts():
    rows = []
    for p in POSTS_DIR.glob("*.html"):
        text = p.read_text(encoding="utf-8", errors="replace")
        title_m = H2_RE.search(text)
        date_m = POSTDATE_RE.search(text)
        desc_m = DESC_META_RE.search(text)
        if not (title_m and date_m):
            continue
        dt = parse_spanish_date(date_m.group(1))
        if not dt:
            continue
        title = strip(title_m.group(1))
        if not title:
            continue
        description = unescape(desc_m.group(1)) if desc_m else ""
        url = SITE_URL + "/site/posts/" + p.stem
        rows.append({
            "title": title,
            "date": dt,
            "description": description,
            "url": url,
            "id": p.stem,
        })
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows[:MAX_ENTRIES]


def build_feed():
    posts = collect_posts()
    updated = posts[0]["date"] if posts else datetime.now(timezone.utc)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="es">',
        f'  <title>Enriqueta Hueso Martínez — Galería O+O</title>',
        f'  <subtitle>Exposiciones y noticias de Galería O+O, Valencia.</subtitle>',
        f'  <link href="{FEED_URL}" rel="self" type="application/atom+xml"/>',
        f'  <link href="{SITE_URL}/" rel="alternate" type="text/html"/>',
        f'  <id>{SITE_URL}/</id>',
        f'  <updated>{updated.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>',
        f'  <icon>{SITE_URL}/img/brand/favicon-192.png</icon>',
        f'  <logo>{SITE_URL}/img/brand/favicon-512.png</logo>',
        f'  <rights>© Enriqueta Hueso Martínez</rights>',
        '  <author>',
        '    <name>Enriqueta Hueso Martínez</name>',
        f'    <uri>{SITE_URL}/</uri>',
        '  </author>',
    ]
    for r in posts:
        lines.extend([
            "  <entry>",
            f'    <title>{xml_escape(r["title"])}</title>',
            f'    <link href="{xml_escape(r["url"])}" rel="alternate" type="text/html"/>',
            f'    <id>{xml_escape(r["url"])}</id>',
            f'    <published>{r["date"].strftime("%Y-%m-%dT%H:%M:%SZ")}</published>',
            f'    <updated>{r["date"].strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>',
            f'    <summary type="text">{xml_escape(r["description"])}</summary>',
            "  </entry>",
        ])
    lines.append("</feed>")
    out = PUBLIC / "feed.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"feed.xml → {len(posts)} entries, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    build_feed()
