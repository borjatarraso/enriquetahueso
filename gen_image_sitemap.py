"""Generate sitemap-images.xml + sitemap-index.xml.

Image sitemap entries: for each indexable HTML page, list its <img>
references (resolved to absolute URLs), with title/caption derived from
alt attribute. Helps Google Images discover the full gallery.

The sitemap index references both sitemap.xml (pages) and
sitemap-images.xml (images) — robots.txt is updated to point at the
index file.
"""
import json
import re
from html import unescape
from pathlib import Path

REPO = Path("/home/overdrive/claude/enriquetahueso")
PUBLIC = REPO / "public"
SITE_URL = "https://enriquetahueso.com"

IMG_RE = re.compile(r'<img\b([^>]*)>', re.IGNORECASE)
SRC_RE = re.compile(r'\bsrc\s*=\s*"([^"]*)"', re.IGNORECASE)
ALT_RE = re.compile(r'\balt\s*=\s*"([^"]*)"', re.IGNORECASE)


def xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def page_url_for(html_path: Path) -> str:
    rel = html_path.relative_to(PUBLIC).as_posix()
    if rel == "index.html":
        return SITE_URL + "/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("/index.html")]
        return f"{SITE_URL}/{rel}"
    if rel.endswith(".html"):
        rel = rel[: -len(".html")]
    return f"{SITE_URL}/{rel}"


def resolve_img_src(src: str, page_path: Path) -> str | None:
    """Convert a relative <img src=...> to an absolute https URL.
    Returns None for empty/data/external invalid sources."""
    src = src.strip()
    if not src:
        return None
    if src.startswith("data:"):
        return None
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("http://") or src.startswith("https://"):
        # External image — skip (sitemap should only contain own assets)
        if "enriquetahueso.com" not in src:
            return None
        return src
    if src.startswith("/"):
        return SITE_URL + src
    # Relative — resolve against the page's directory
    page_dir = page_path.parent
    resolved = (page_dir / src).resolve()
    try:
        rel = resolved.relative_to(PUBLIC).as_posix()
    except ValueError:
        return None
    return SITE_URL + "/" + rel


def collect_image_entries():
    """Returns dict[page_url] → list[dict(loc, title)]."""
    entries: dict[str, list[dict]] = {}
    for p in sorted(PUBLIC.rglob("*.html")):
        rel = p.relative_to(PUBLIC).as_posix()
        if rel.startswith("docs/"):
            continue
        page_url = page_url_for(p)
        text = p.read_text(encoding="utf-8", errors="replace")
        page_imgs = []
        seen = set()
        for m in IMG_RE.finditer(text):
            attrs = m.group(1)
            src_m = SRC_RE.search(attrs)
            if not src_m:
                continue
            src = src_m.group(1)
            abs_src = resolve_img_src(src, p)
            if not abs_src or abs_src in seen:
                continue
            # Skip broken-img marker (src="" with class broken-img)
            if not src:
                continue
            seen.add(abs_src)
            alt_m = ALT_RE.search(attrs)
            title = unescape(alt_m.group(1)).strip() if alt_m else ""
            page_imgs.append({"loc": abs_src, "title": title})
        if page_imgs:
            entries[page_url] = page_imgs
    return entries


def build_image_sitemap():
    entries = collect_image_entries()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
    img_count = 0
    for page_url, imgs in entries.items():
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(page_url)}</loc>")
        for img in imgs:
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{xml_escape(img['loc'])}</image:loc>")
            if img["title"]:
                lines.append(f"      <image:title>{xml_escape(img['title'])}</image:title>")
                lines.append(f"      <image:caption>{xml_escape(img['title'])}</image:caption>")
            lines.append("    </image:image>")
            img_count += 1
        lines.append("  </url>")
    lines.append("</urlset>")
    out = PUBLIC / "sitemap-images.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap-images.xml → {len(entries)} pages, {img_count} images, "
          f"{out.stat().st_size // 1024} KB")
    return img_count


def build_sitemap_index():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for name in ("sitemap.xml", "sitemap-images.xml"):
        lines.append("  <sitemap>")
        lines.append(f"    <loc>{SITE_URL}/{name}</loc>")
        lines.append("  </sitemap>")
    lines.append("</sitemapindex>")
    out = PUBLIC / "sitemap-index.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap-index.xml → {out.stat().st_size} B")


def update_robots():
    body = f"""# enriquetahueso.com — robots.txt
User-agent: *
Allow: /

# Block Cloudflare-injected challenge endpoints (defensive)
Disallow: /cdn-cgi/

Sitemap: {SITE_URL}/sitemap-index.xml
Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/sitemap-images.xml
"""
    out = PUBLIC / "robots.txt"
    out.write_text(body, encoding="utf-8")
    print(f"robots.txt → {out.stat().st_size} B")


if __name__ == "__main__":
    build_image_sitemap()
    build_sitemap_index()
    update_robots()
