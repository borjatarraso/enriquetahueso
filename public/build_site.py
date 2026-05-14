#!/usr/bin/env python3
"""
Build a clean static site from the downloaded Blogger content.
Extracts actual content from Blogger HTML and generates a modern site.
"""
import os
import re
import html
import shutil
from datetime import datetime

SRC = "www.galeriaomaso.com"
DEST = "site"

# Color scheme from original site
COLORS = {
    "bg_dark": "#37021c",      # Dark maroon background
    "accent": "#ffd966",       # Gold accent
    "text_light": "#ffffff",
    "text_hover": "#741b47",   # Purple hover
    "card_bg": "#4a0a2e",      # Slightly lighter maroon for cards
    "border": "#6b1d42",
}

def extract_post_body(html_content):
    """Extract the main content from a Blogger post."""
    # Try multiple patterns
    patterns = [
        r"<div class='post-body[^']*'[^>]*>(.*?)</div>\s*(?:<div class='post-footer'|<div class='blog-pager')",
        r"<div class='post-body[^']*'[^>]*>(.*?)</div>\s*<div",
    ]
    for pattern in patterns:
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            body = match.group(1).strip()
            if len(body) > 10:
                return body
    return None

def extract_post_title(html_content):
    """Extract post title."""
    match = re.search(r"<h3 class='post-title[^']*'[^>]*>(.*?)</h3>", html_content, re.DOTALL)
    if match:
        title = match.group(1).strip()
        # Remove link tags
        title = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', title, flags=re.DOTALL)
        title = re.sub(r'<[^>]+>', '', title).strip()
        return html.unescape(title) if title else None

    # Try og:title
    match = re.search(r"property='og:title'\s*content='([^']*)'", html_content)
    if not match:
        match = re.search(r"content='([^']*)'\s*property='og:title'", html_content)
    if match:
        title = match.group(1).strip()
        if title and title != "Galeria O+O":
            return html.unescape(title)
    return None

def extract_date(html_content):
    """Extract post date."""
    match = re.search(r"<h2 class='date-header'[^>]*><span>(.*?)</span>", html_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_page_title(html_content):
    """Extract page title from og:title."""
    match = re.search(r"content='([^']*)'\s*property='og:title'", html_content)
    if not match:
        match = re.search(r"property='og:title'\s*content='([^']*)'", html_content)
    if match:
        return html.unescape(match.group(1).strip())
    return None

def extract_og_image(html_content):
    """Extract og:image."""
    match = re.search(r"content='([^']*)'\s*property='og:image'", html_content)
    if not match:
        match = re.search(r"property='og:image'\s*content='([^']*)'", html_content)
    if match:
        return match.group(1).strip()
    return None

def extract_first_image(html_content):
    """Extract first image src from content."""
    match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', html_content)
    if match:
        return match.group(1)
    return None

def fix_image_paths(content, depth):
    """Fix image paths to be relative to site root."""
    prefix = "../" * depth
    # Fix paths like ../images/ or ../../images/ etc
    content = re.sub(r'(?:\.\./)+images/', prefix + 'images/', content)
    return content

def clean_content(body):
    """Clean up Blogger-specific markup."""
    if not body:
        return ""
    # Remove clear divs
    body = re.sub(r"<div style='clear: both;'></div>", "", body)
    # Remove empty divs/spans
    body = re.sub(r'<div[^>]*>\s*</div>', '', body)
    body = re.sub(r'<span[^>]*>\s*</span>', '', body)
    # Clean up excessive br tags
    body = re.sub(r'(<br\s*/?>){3,}', '<br><br>', body)
    # Remove blogger separator class but keep content
    body = re.sub(r'class="separator"', '', body)
    return body.strip()

def get_nav_html(active=""):
    """Generate navigation HTML."""
    pages = [
        ("index.html", "Inicio"),
        ("exposiciones.html", "Exposiciones"),
        ("artistas.html", "Artistas"),
        ("articulos.html", "Artículos"),
        ("internacional.html", "Internacional"),
        ("ferias.html", "Ferias"),
        ("cursos.html", "Cursos"),
        ("noticias.html", "Noticias"),
        ("enlaces.html", "Enlaces"),
        ("contacta.html", "Contacto"),
    ]
    items = []
    for href, label in pages:
        cls = ' class="active"' if label == active else ""
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return "\n".join(items)

def page_template(title, content, active="", description=""):
    """Generate a full HTML page."""
    nav = get_nav_html(active)
    desc = description or "Galería O+O - Centro de referencia internacional de arte entre Oriente y Occidente. Valencia, España."
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Galería O+O 东西方画廊</title>
    <meta name="description" content="{desc}">
    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="header-inner">
            <a href="index.html" class="logo">
                <h1>Galería O<span class="plus">+</span>O</h1>
                <p class="subtitle">东西方画廊（西班牙—中国）</p>
            </a>
        </div>
        <nav>
            <button class="menu-toggle" aria-label="Menú">&#9776;</button>
            <div class="nav-links">
                {nav}
            </div>
        </nav>
    </header>
    <main>
        {content}
    </main>
    <footer>
        <div class="footer-inner">
            <p>Galería O+O &middot; 东西方画廊（西班牙—中国）</p>
            <p>C/ Francisco Martínez nº 34 - 36 Bajo, 46020 Valencia (España)</p>
            <p><a href="mailto:enriqueta.hueso@gmail.com">enriqueta.hueso@gmail.com</a> &middot; (+34) 639 99 03 92</p>
        </div>
    </footer>
    <script>
        document.querySelector('.menu-toggle').addEventListener('click', function() {{
            document.querySelector('.nav-links').classList.toggle('open');
        }});
    </script>
</body>
</html>"""

def get_css():
    return """/* Galería O+O - Static Site Styles */
:root {
    --bg-dark: #37021c;
    --bg-card: #4a0a2e;
    --accent: #ffd966;
    --text: #ffffff;
    --text-muted: #d4a0b8;
    --hover: #741b47;
    --border: #6b1d42;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Georgia', 'Palatino Linotype', serif;
    background: var(--bg-dark);
    color: var(--text);
    line-height: 1.7;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

a { color: var(--accent); text-decoration: none; transition: color 0.2s; }
a:hover { color: #fff; text-decoration: underline; }

img { max-width: 100%; height: auto; border-radius: 4px; }

/* Header */
header {
    background: linear-gradient(135deg, #2a0115 0%, #37021c 50%, #4a0a2e 100%);
    border-bottom: 2px solid var(--accent);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.2rem 2rem 0.5rem;
    text-align: center;
}

.logo { color: var(--text); text-decoration: none; }
.logo:hover { text-decoration: none; color: var(--accent); }

.logo h1 {
    font-size: 2.2rem;
    font-weight: normal;
    letter-spacing: 3px;
}

.logo .plus { color: var(--accent); font-weight: bold; }

.subtitle {
    font-size: 0.95rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

/* Navigation */
nav {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.5rem 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
}

.menu-toggle {
    display: none;
    background: none;
    border: 1px solid var(--accent);
    color: var(--accent);
    font-size: 1.5rem;
    padding: 0.3rem 0.8rem;
    cursor: pointer;
    border-radius: 4px;
}

.nav-links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.2rem;
    justify-content: center;
}

.nav-links a {
    color: var(--text-muted);
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.2s;
}

.nav-links a:hover, .nav-links a.active {
    color: var(--accent);
    background: rgba(255, 217, 102, 0.1);
    text-decoration: none;
}

/* Main */
main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    flex: 1;
    width: 100%;
}

/* Page header */
.page-header {
    text-align: center;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}

.page-header h2 {
    font-size: 2rem;
    font-weight: normal;
    color: var(--accent);
    letter-spacing: 2px;
}

/* Post grid */
.post-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
}

.post-card {
    background: var(--bg-card);
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
    transition: transform 0.2s, border-color 0.2s;
}

.post-card:hover {
    transform: translateY(-3px);
    border-color: var(--accent);
}

.post-card a { text-decoration: none; }

.post-card-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
}

.post-card-body {
    padding: 1.2rem;
}

.post-card-body h3 {
    font-size: 1.1rem;
    font-weight: normal;
    color: var(--accent);
    margin-bottom: 0.5rem;
    line-height: 1.3;
}

.post-card-date {
    font-size: 0.8rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Single post / page content */
.page-content {
    background: var(--bg-card);
    border-radius: 8px;
    padding: 2rem;
    border: 1px solid var(--border);
    max-width: 900px;
    margin: 0 auto;
}

.page-content h2, .page-content h3 {
    color: var(--accent);
    margin: 1.5rem 0 0.8rem;
}

.page-content p { margin-bottom: 1rem; }

.page-content img {
    display: block;
    margin: 1.5rem auto;
    max-height: 600px;
}

.page-content a { color: var(--accent); }

.post-date {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.post-nav {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}

.post-nav a {
    color: var(--accent);
    font-size: 0.9rem;
}

/* Hero section (homepage) */
.hero {
    text-align: center;
    padding: 3rem 1rem;
    margin-bottom: 2rem;
}

.hero h2 {
    font-size: 1.6rem;
    font-weight: normal;
    color: var(--text);
    margin-bottom: 0.8rem;
}

.hero p {
    color: var(--text-muted);
    max-width: 700px;
    margin: 0 auto;
    font-size: 1.05rem;
}

/* Year group headers */
.year-header {
    font-size: 1.5rem;
    color: var(--accent);
    font-weight: normal;
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* Footer */
footer {
    background: linear-gradient(135deg, #1a010d, #2a0115);
    border-top: 2px solid var(--accent);
    text-align: center;
    padding: 1.5rem 2rem;
    margin-top: 3rem;
}

.footer-inner p {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin: 0.3rem 0;
}

.footer-inner a { color: var(--accent); }

/* Back to top / utility */
.back-link {
    display: inline-block;
    margin-bottom: 1.5rem;
    color: var(--text-muted);
    font-size: 0.9rem;
}

.back-link:hover { color: var(--accent); }

/* Responsive */
@media (max-width: 768px) {
    .logo h1 { font-size: 1.6rem; }
    .subtitle { font-size: 0.8rem; }

    .menu-toggle { display: block; }

    nav { justify-content: flex-end; }

    .nav-links {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: #2a0115;
        flex-direction: column;
        padding: 0.5rem;
        border-bottom: 2px solid var(--accent);
    }

    .nav-links.open { display: flex; }

    .nav-links a {
        padding: 0.8rem 1rem;
        border-bottom: 1px solid var(--border);
    }

    main { padding: 1rem; }

    .post-grid {
        grid-template-columns: 1fr;
    }

    .page-content { padding: 1.2rem; }

    .hero { padding: 2rem 0.5rem; }
    .hero h2 { font-size: 1.3rem; }
}

/* Loading placeholder for images */
.post-card-image[src=""] {
    background: var(--border);
}

/* Smooth scrolling */
html { scroll-behavior: smooth; }
"""

def build():
    """Build the static site."""
    # Create output directory
    if os.path.exists(DEST):
        shutil.rmtree(DEST)
    os.makedirs(DEST)

    # Copy images and assets
    shutil.copytree(f"{SRC}/images", f"{DEST}/images")
    shutil.copytree(f"{SRC}/assets", f"{DEST}/assets")
    if os.path.exists(f"{SRC}/favicon.ico"):
        shutil.copy2(f"{SRC}/favicon.ico", f"{DEST}/favicon.ico")

    # Write CSS
    with open(f"{DEST}/style.css", "w") as f:
        f.write(get_css())

    # Process static pages
    page_map = {
        "artistas.html": ("Artistas", "Artistas"),
        "articulos.html": ("Artículos", "Artículos"),
        "blog-page.html": ("Internacional", "Internacional"),
        "blog-page_12.html": ("Ferias", "Ferias"),
        "cursos.html": ("Cursos", "Cursos"),
        "noticias.html": ("Noticias", "Noticias"),
        "enlaces.html": ("Enlaces", "Enlaces"),
        "contacta.html": ("Contacto", "Contacto"),
        "como-llegar.html": ("Cómo llegar", "Contacto"),
    }

    for src_file, (title, nav_active) in page_map.items():
        src_path = f"{SRC}/p/{src_file}"
        if not os.path.exists(src_path):
            continue

        with open(src_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        body = extract_post_body(content)
        if not body:
            continue

        body = clean_content(body)
        # Fix image paths (from p/ directory, images are at ../images/)
        body = body.replace('../images/', 'images/')

        # Remap output filename
        out_name = src_file
        if src_file == "blog-page.html":
            out_name = "internacional.html"
        elif src_file == "blog-page_12.html":
            out_name = "ferias.html"
        elif src_file == "como-llegar.html":
            out_name = "como-llegar.html"

        page_html = f"""<div class="page-header"><h2>{title}</h2></div>
<div class="page-content">
{body}
</div>"""

        full = page_template(title, page_html, active=nav_active)
        with open(f"{DEST}/{out_name}", "w", encoding="utf-8") as f:
            f.write(full)

        print(f"  Page: {out_name} ({title})")

    # Process blog posts
    posts = []
    post_files = []
    for root, dirs, files in os.walk(SRC):
        for fname in files:
            if fname.endswith('.html'):
                path = os.path.join(root, fname)
                # Only process year/month/post.html files (actual posts)
                parts = path.replace(SRC + '/', '').split('/')
                if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                    # Skip index.html files in year/month dirs
                    if fname == 'index.html':
                        continue
                    post_files.append(path)

    print(f"\nProcessing {len(post_files)} blog posts...")

    for path in post_files:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        title = extract_post_title(content)
        date = extract_date(content)
        body = extract_post_body(content)
        og_image = extract_og_image(content)

        if not title and not body:
            continue

        if not title:
            title = "Sin título"

        # Extract year/month from path
        rel_path = path.replace(SRC + '/', '')
        parts = rel_path.split('/')
        year = parts[0]
        month = parts[1]
        slug = os.path.splitext(parts[-1])[0]

        # Get thumbnail image
        thumb = None
        if og_image:
            thumb = og_image
            # Fix relative paths
            if thumb.startswith('../'):
                thumb = thumb.replace('../images/', 'images/')
            elif thumb.startswith('images/'):
                pass
            elif not thumb.startswith('http'):
                thumb = f"images/{os.path.basename(thumb)}"
        elif body:
            first_img = extract_first_image(body)
            if first_img:
                thumb = first_img
                if thumb.startswith('../'):
                    thumb = thumb.replace('../images/', 'images/')

        posts.append({
            'title': title,
            'date': date or f"{year}/{month}",
            'year': year,
            'month': month,
            'slug': slug,
            'body': body,
            'thumb': thumb,
            'filename': f"post-{year}-{month}-{slug}.html",
        })

    # Sort posts by year/month descending
    posts.sort(key=lambda p: (p['year'], p['month']), reverse=True)

    # Generate individual post pages
    os.makedirs(f"{DEST}/posts", exist_ok=True)
    for i, post in enumerate(posts):
        body = clean_content(post['body'] or '')
        # Fix image paths
        body = re.sub(r'(?:\.\./)+images/', '../images/', body)

        prev_link = ""
        next_link = ""
        if i > 0:
            next_link = f'<a href="{posts[i-1]["filename"]}">&larr; Siguiente</a>'
        if i < len(posts) - 1:
            prev_link = f'<a href="{posts[i+1]["filename"]}">Anterior &rarr;</a>'

        post_html = f"""<a href="../exposiciones.html" class="back-link">&larr; Volver a exposiciones</a>
<div class="page-content">
    <h2 style="color: var(--accent); margin-bottom: 0.5rem;">{post['title']}</h2>
    <p class="post-date">{post['date']}</p>
    {body}
    <div class="post-nav">
        {prev_link}
        {next_link}
    </div>
</div>"""

        full = page_template(post['title'], post_html, active="Exposiciones")
        # Fix paths for posts/ subdirectory
        full = full.replace('href="index.html"', 'href="../index.html"')
        full = full.replace('href="exposiciones.html"', 'href="../exposiciones.html"')
        full = full.replace('href="artistas.html"', 'href="../artistas.html"')
        full = full.replace('href="articulos.html"', 'href="../articulos.html"')
        full = full.replace('href="internacional.html"', 'href="../internacional.html"')
        full = full.replace('href="ferias.html"', 'href="../ferias.html"')
        full = full.replace('href="cursos.html"', 'href="../cursos.html"')
        full = full.replace('href="noticias.html"', 'href="../noticias.html"')
        full = full.replace('href="enlaces.html"', 'href="../enlaces.html"')
        full = full.replace('href="contacta.html"', 'href="../contacta.html"')
        full = full.replace('href="como-llegar.html"', 'href="../como-llegar.html"')
        full = full.replace('href="style.css"', 'href="../style.css"')
        full = full.replace('href="favicon.ico"', 'href="../favicon.ico"')

        with open(f"{DEST}/posts/{post['filename']}", "w", encoding="utf-8") as f:
            f.write(full)

    print(f"  Generated {len(posts)} post pages")

    # Generate exposiciones (blog listing) page
    cards_html = []
    current_year = None
    for post in posts:
        if post['year'] != current_year:
            current_year = post['year']
            cards_html.append(f'</div><h3 class="year-header">{current_year}</h3><div class="post-grid">')

        thumb_html = ""
        if post['thumb']:
            thumb_src = post['thumb']
            if not thumb_src.startswith('http') and not thumb_src.startswith('images/'):
                thumb_src = re.sub(r'^(\.\./)+', '', thumb_src)
            thumb_html = f'<img class="post-card-image" src="{thumb_src}" alt="" loading="lazy">'

        cards_html.append(f"""<div class="post-card">
    <a href="posts/{post['filename']}">
        {thumb_html}
        <div class="post-card-body">
            <h3>{post['title']}</h3>
            <span class="post-card-date">{post['date']}</span>
        </div>
    </a>
</div>""")

    expo_content = f"""<div class="page-header"><h2>Exposiciones</h2></div>
<div class="post-grid">
{"".join(cards_html)}
</div>"""

    full = page_template("Exposiciones", expo_content, active="Exposiciones")
    with open(f"{DEST}/exposiciones.html", "w", encoding="utf-8") as f:
        f.write(full)

    # Generate homepage
    # Show latest 6 posts
    latest_cards = []
    for post in posts[:6]:
        thumb_html = ""
        if post['thumb']:
            thumb_src = post['thumb']
            if not thumb_src.startswith('http') and not thumb_src.startswith('images/'):
                thumb_src = re.sub(r'^(\.\./)+', '', thumb_src)
            thumb_html = f'<img class="post-card-image" src="{thumb_src}" alt="" loading="lazy">'

        latest_cards.append(f"""<div class="post-card">
    <a href="posts/{post['filename']}">
        {thumb_html}
        <div class="post-card-body">
            <h3>{post['title']}</h3>
            <span class="post-card-date">{post['date']}</span>
        </div>
    </a>
</div>""")

    home_content = f"""<div class="hero">
    <h2>Gestión Cultural O+O</h2>
    <p>Centro de referencia internacional. Su idea se forma a partir de distintas culturas plásticas entre Oriente y Occidente, tomando esta mezcla como unicidad. Un intercambio cultural encaminado hacia la difusión del arte y la cultura, hacia la promoción artística de los artistas y sus obras.</p>
</div>

<div class="page-header"><h2>Últimas Exposiciones</h2></div>
<div class="post-grid">
{"".join(latest_cards)}
</div>
<div style="text-align: center; margin-top: 2rem;">
    <a href="exposiciones.html" style="color: var(--accent); font-size: 1.1rem;">Ver todas las exposiciones &rarr;</a>
</div>"""

    full = page_template("Inicio", home_content, active="Inicio")
    with open(f"{DEST}/index.html", "w", encoding="utf-8") as f:
        f.write(full)

    print(f"\nSite built successfully!")
    print(f"  Pages: {len(page_map)} static + {len(posts)} posts + 2 (home, exposiciones)")
    print(f"  Output: {DEST}/")

if __name__ == "__main__":
    build()
