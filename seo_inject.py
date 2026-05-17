"""Inject SEO meta into legacy site pages.

Adds: canonical, og:* (type, site_name, title, description, url, image,
locale), twitter:card, robots, theme-color, favicon links.

Per-page title + description for top-level pages. Posts get a generic
article description; they get canonical + OG so social shares render.

Mirrors changes to both site/ and public/site/.
"""
import re
from pathlib import Path

REPO = Path("/home/overdrive/claude/enriquetahueso")
ROOTS = [REPO / "site", REPO / "public" / "site"]
SITE_URL = "https://enriquetahueso.com"
OG_IMAGE = f"{SITE_URL}/img/brand/og-image.jpg"

# Per-page (title, description) for top-level legacy pages.
TOP_LEVEL = {
    "index": (
        "Galería O+O — Centro de arte entre Oriente y Occidente | Valencia",
        "Galería O+O (东西方画廊) — espacio de referencia internacional de arte entre Oriente y Occidente. Fundada en Valencia por Enriqueta Hueso Martínez.",
    ),
    "artistas": (
        "Artistas | Galería O+O",
        "Artistas representados por Galería O+O: creadores españoles, chinos, japoneses y de otros países en un diálogo entre Oriente y Occidente.",
    ),
    "articulos": (
        "Artículos | Galería O+O",
        "Artículos, ensayos y publicaciones sobre arte contemporáneo, intercambios culturales y la trayectoria de Galería O+O.",
    ),
    "exposiciones": (
        "Exposiciones | Galería O+O",
        "Catálogo de exposiciones celebradas en Galería O+O — pintura, grabado, escultura, fotografía y videoarte de artistas internacionales.",
    ),
    "internacional": (
        "Proyectos internacionales | Galería O+O",
        "Intercambios culturales y proyectos internacionales de Galería O+O entre España, China, Japón, India y otros países.",
    ),
    "ferias": (
        "Ferias de arte | Galería O+O",
        "Participación de Galería O+O y sus artistas en ferias internacionales de arte contemporáneo.",
    ),
    "cursos": (
        "Cursos y formación | Galería O+O",
        "Cursos, talleres y programas formativos impartidos en Galería O+O sobre pintura, grabado y arte oriental.",
    ),
    "noticias": (
        "Noticias | Galería O+O",
        "Noticias, novedades y actualidad de Galería O+O: exposiciones, premios, publicaciones y eventos culturales.",
    ),
    "enlaces": (
        "Enlaces de interés | Galería O+O",
        "Enlaces a recursos, instituciones y proyectos relacionados con Galería O+O y el arte entre Oriente y Occidente.",
    ),
    "contacta": (
        "Contacto | Galería O+O",
        "Información de contacto de Galería O+O: dirección en Valencia, teléfono y correo electrónico.",
    ),
    "como-llegar": (
        "Cómo llegar | Galería O+O",
        "Cómo llegar a Galería O+O: ubicación, mapa y medios de transporte. C/ Francisco Martínez 34-36, Valencia.",
    ),
}

POST_DESC_DEFAULT = (
    "Galería O+O (东西方画廊) — espacio de arte entre Oriente y Occidente en "
    "Valencia, fundado por Enriqueta Hueso Martínez."
)


def rel_url_path(file_path: Path, root: Path) -> str:
    """For file_path under root (either site/ or public/site/), return the
    URL path beginning with /site/... (Cloudflare strips .html)."""
    rel = file_path.relative_to(root).as_posix()  # e.g. 'artistas.html' or 'posts/post-x.html'
    if rel == "index.html":
        return "/site/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("/index.html")]
        return f"/site/{rel}"
    if rel.endswith(".html"):
        rel = rel[: -len(".html")]
    return f"/site/{rel}"


def is_post(file_path: Path, root: Path) -> bool:
    rel = file_path.relative_to(root).as_posix()
    return rel.startswith("posts/")


def extract_existing_title(head: str) -> str | None:
    m = re.search(r"<title>(.*?)</title>", head, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else None


def html_attr_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


SEO_MARKER = "<!-- SEO-META-INJECTED -->"


def build_meta_block(canonical_url: str, title: str, description: str,
                     is_article: bool) -> str:
    og_type = "article" if is_article else "website"
    lines = [
        '    <meta name="robots" content="index, follow, max-image-preview:large">',
        '    <meta name="theme-color" content="#181210">',
        f'    <link rel="canonical" href="{canonical_url}">',
        '',
        '    <!-- Open Graph -->',
        f'    <meta property="og:type" content="{og_type}">',
        '    <meta property="og:site_name" content="Galería O+O (东西方画廊)">',
        f'    <meta property="og:title" content="{html_attr_escape(title)}">',
        f'    <meta property="og:description" content="{html_attr_escape(description)}">',
        f'    <meta property="og:url" content="{canonical_url}">',
        f'    <meta property="og:image" content="{OG_IMAGE}">',
        '    <meta property="og:image:width" content="1200">',
        '    <meta property="og:image:height" content="630">',
        '    <meta property="og:locale" content="es_ES">',
        '',
        '    <!-- Twitter Card -->',
        '    <meta name="twitter:card" content="summary_large_image">',
        f'    <meta name="twitter:title" content="{html_attr_escape(title)}">',
        f'    <meta name="twitter:description" content="{html_attr_escape(description)}">',
        f'    <meta name="twitter:image" content="{OG_IMAGE}">',
        '',
        '    <!-- Favicons (brand set) -->',
        '    <link rel="icon" type="image/svg+xml" href="/img/brand/favicon.svg">',
        '    <link rel="icon" type="image/png" sizes="32x32" href="/img/brand/favicon-32.png">',
        '    <link rel="icon" type="image/png" sizes="16x16" href="/img/brand/favicon-16.png">',
        '    <link rel="apple-touch-icon" sizes="180x180" href="/img/brand/apple-touch-icon.png">',
        '    <link rel="manifest" href="/site.webmanifest">',
    ]
    return "\n".join(lines)


def inject(file_path: Path, root: Path) -> bool:
    text = file_path.read_text(encoding="utf-8")
    if SEO_MARKER in text:
        return False

    canonical_url = SITE_URL + rel_url_path(file_path, root)
    stem = file_path.stem
    post = is_post(file_path, root)
    existing_title = extract_existing_title(text)

    if post:
        title = existing_title or "Galería O+O (东西方画廊)"
        description = POST_DESC_DEFAULT
    else:
        meta = TOP_LEVEL.get(stem)
        if meta:
            new_title, description = meta
            title = new_title
            # Replace <title>
            text = re.sub(
                r"<title>.*?</title>",
                f"<title>{new_title}</title>",
                text, count=1, flags=re.DOTALL | re.IGNORECASE,
            )
            # Replace description
            text = re.sub(
                r'<meta\s+name="description"[^>]*>',
                f'<meta name="description" content="{html_attr_escape(description)}">',
                text, count=1, flags=re.IGNORECASE,
            )
        else:
            title = existing_title or "Galería O+O (东西方画廊)"
            description = POST_DESC_DEFAULT

    block = build_meta_block(canonical_url, title, description, is_article=post)
    block = f"    {SEO_MARKER}\n{block}\n"

    new_text, n = re.subn(
        r'(\s*<link rel="stylesheet"[^>]*>)',
        lambda m: "\n" + block + m.group(1),
        text, count=1,
    )
    if n == 0:
        new_text = re.sub(
            r"</head>", block + "</head>", text, count=1, flags=re.IGNORECASE,
        )

    # Remove the old relative favicon.ico link — superseded by the brand set.
    new_text = re.sub(
        r'\s*<link rel="icon" href="favicon\.ico"[^>]*>',
        "",
        new_text,
    )

    file_path.write_text(new_text, encoding="utf-8")
    return True


def main():
    total = 0
    posts = 0
    by_root = {}
    for root in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*.html")):
            if inject(p, root):
                total += 1
                if is_post(p, root):
                    posts += 1
        by_root[root] = sum(1 for _ in root.rglob("*.html"))
    print(f"Injected SEO meta into {total} files ({posts} posts).")
    for r, n in by_root.items():
        print(f"  {r}: {n} html files total")


if __name__ == "__main__":
    main()
