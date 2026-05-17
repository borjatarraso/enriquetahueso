"""Add meaningful alt text + loading="lazy" to legacy site images.

Strategy:
- For each HTML page, derive a fallback alt from the page <h2> (or <title>).
- For <img> tags with NO alt attribute → add alt=fallback.
- For <img> tags with empty alt='' → leave alone (might be intentionally
  decorative). Empty alt is a valid pattern; we don't overwrite it.
- For <img> tags without loading attribute → add loading="lazy".

Mirrors changes to both site/ and public/site/.
"""
import re
from pathlib import Path

REPO = Path("/home/overdrive/claude/enriquetahueso")
ROOTS = [REPO / "site", REPO / "public" / "site"]


def derive_fallback_alt(html_text: str, file_path: Path) -> str:
    # Prefer the page <h2> (which is the post/page title in this layout)
    m = re.search(r"<h2[^>]*>(.*?)</h2>", html_text, re.DOTALL | re.IGNORECASE)
    if m:
        raw = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if raw:
            return raw
    m = re.search(r"<title>(.*?)</title>", html_text, re.DOTALL | re.IGNORECASE)
    if m:
        raw = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        # Strip the " | Galería O+O" suffix for cleaner alt
        raw = re.sub(r"\s*\|\s*Galer[ií]a.*$", "", raw)
        if raw:
            return raw
    return "Galería O+O — Enriqueta Hueso Martínez"


def html_attr_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;")


IMG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)


def process_img(tag_attrs: str, fallback_alt: str) -> str:
    """tag_attrs is the inner attribute string of <img ...>."""
    attrs = tag_attrs
    added = []

    has_alt = re.search(r"\balt\s*=", attrs, re.IGNORECASE)
    has_loading = re.search(r"\bloading\s*=", attrs, re.IGNORECASE)
    has_decoding = re.search(r"\bdecoding\s*=", attrs, re.IGNORECASE)

    if not has_alt:
        added.append(f'alt="{html_attr_escape(fallback_alt)}"')
    if not has_loading:
        added.append('loading="lazy"')
    if not has_decoding:
        added.append('decoding="async"')

    if not added:
        return f"<img{attrs}>"

    # Trim trailing whitespace before injecting
    attrs = attrs.rstrip()
    return f"<img {' '.join(added)}{attrs}>"


def process_file(p: Path) -> tuple[int, int]:
    text = p.read_text(encoding="utf-8", errors="replace")
    fallback = derive_fallback_alt(text, p)

    counts = {"alt_added": 0, "loading_added": 0}

    def repl(m):
        before = m.group(1)
        had_alt = bool(re.search(r"\balt\s*=", before, re.IGNORECASE))
        had_loading = bool(re.search(r"\bloading\s*=", before, re.IGNORECASE))
        if not had_alt:
            counts["alt_added"] += 1
        if not had_loading:
            counts["loading_added"] += 1
        return process_img(before, fallback)

    new_text, n = IMG_RE.subn(repl, text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
    return counts["alt_added"], counts["loading_added"]


def main():
    files = 0
    total_alt = 0
    total_lazy = 0
    for root in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*.html")):
            a, l = process_file(p)
            if a or l:
                files += 1
                total_alt += a
                total_lazy += l
    print(f"Files modified: {files}")
    print(f"  alt attributes added: {total_alt}")
    print(f"  loading='lazy' added: {total_lazy}")


if __name__ == "__main__":
    main()
