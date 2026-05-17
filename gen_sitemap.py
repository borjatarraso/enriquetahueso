"""Generate sitemap.xml + robots.txt for enriquetahueso.com.

Walks public/ for HTML pages, emits canonical URLs (no .html suffix
since Cloudflare Pages strips it via 307). Outputs to public/sitemap.xml
and public/robots.txt.
"""
import datetime
import re
from pathlib import Path

ROOT = Path("/home/overdrive/claude/enriquetahueso/public")
SITE_URL = "https://enriquetahueso.com"

# Pages with explicit priority / changefreq tuning
TUNING = {
    "/": (1.0, "weekly"),
    "/site/artistas": (0.9, "monthly"),
    "/site/exposiciones": (0.9, "monthly"),
    "/site/articulos": (0.8, "monthly"),
    "/site/internacional": (0.8, "monthly"),
    "/site/noticias": (0.8, "weekly"),
    "/site/ferias": (0.7, "monthly"),
    "/site/cursos": (0.7, "monthly"),
    "/site/enlaces": (0.5, "yearly"),
    "/site/contacta": (0.6, "yearly"),
    "/site/como-llegar": (0.5, "yearly"),
}

# Excluded paths (admin-ish or duplicates)
EXCLUDE_GLOBS = ("docs/**/*.html",)


def url_for(html_path: Path) -> str:
    rel = html_path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    # strip trailing /index.html
    if rel.endswith("/index.html"):
        rel = rel[: -len("/index.html")]
        return "/" + rel
    # strip .html (CF Pages canonical form)
    if rel.endswith(".html"):
        rel = rel[: -len(".html")]
    return "/" + rel


def lastmod_for(p: Path) -> str:
    # File mtime → YYYY-MM-DD
    ts = datetime.datetime.fromtimestamp(p.stat().st_mtime, tz=datetime.timezone.utc)
    return ts.strftime("%Y-%m-%d")


def collect_pages():
    pages = []
    excluded = set()
    for pat in EXCLUDE_GLOBS:
        excluded.update(ROOT.glob(pat))
    for p in sorted(ROOT.rglob("*.html")):
        if p in excluded:
            continue
        rel = p.relative_to(ROOT).as_posix()
        # Skip anything under docs/
        if rel.startswith("docs/"):
            continue
        pages.append(p)
    return pages


def priority_for(url: str, html_path: Path) -> tuple[float, str]:
    if url in TUNING:
        return TUNING[url]
    if url.startswith("/site/posts/"):
        return (0.5, "yearly")
    return (0.6, "monthly")


def build_sitemap():
    pages = collect_pages()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')

    # Languages supported (Google Translate widget covers the rest, but we
    # declare alternates so Google understands the multilingual intent).
    # We use the user-language toggle that sets the googtrans cookie;
    # alternate URLs are the same path (no per-language route).
    # To remain honest, we only declare hreflang on the canonical root.

    for p in pages:
        url = url_for(p)
        loc = SITE_URL + url
        lastmod = lastmod_for(p)
        prio, freq = priority_for(url, p)
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio:.1f}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    out = ROOT / "sitemap.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap.xml → {len(pages)} URLs, {out.stat().st_size // 1024} KB")


def build_robots():
    body = f"""# enriquetahueso.com — robots.txt
User-agent: *
Allow: /

# Block Cloudflare-injected challenge endpoints (defensive)
Disallow: /cdn-cgi/

Sitemap: {SITE_URL}/sitemap.xml
"""
    out = ROOT / "robots.txt"
    out.write_text(body, encoding="utf-8")
    print(f"robots.txt → {out.stat().st_size} B")


if __name__ == "__main__":
    build_sitemap()
    build_robots()
