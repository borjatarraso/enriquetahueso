#!/usr/bin/env python3
"""
Sanitize all HTML in site/ folder:
1. Strip dangerous inline styles from post content
2. Remove broken blogspot image references
3. Fix generic "Galeria O+O" titles
4. Fix inline color styles that conflict with dark theme
5. Clean up Blogger cruft
6. Fix contact page inline styles
"""

import os
import re
import html
from pathlib import Path

SITE_DIR = Path(__file__).parent / "site"
POSTS_DIR = SITE_DIR / "posts"

# Inline style properties that break the dark theme
STRIP_STYLE_PROPS = re.compile(
    r'(?:background(?:-color)?|color|font-family|font-size|vertical-align|'
    r'text-size-adjust|outline|margin|padding)\s*:\s*[^;]+;?\s*',
    re.IGNORECASE
)

# Full style attributes that are just color/font overrides
REMOVE_STYLE_ATTR = re.compile(
    r'\s*style="[^"]*"',
    re.IGNORECASE
)

# Broken blogspot image URLs
BROKEN_IMG_PATTERN = re.compile(
    r'<img[^>]*src="https?://[0-9]+\.bp\.blogspot\.com/[^"]*"[^>]*/?>',
    re.IGNORECASE | re.DOTALL
)

# Broken googleusercontent proxy URLs
BROKEN_PROXY_PATTERN = re.compile(
    r'https://lh3\.googleusercontent\.com/blogger_img_proxy/[^"\'>\s]+',
    re.IGNORECASE
)

# Empty divs and excessive whitespace
EMPTY_DIV = re.compile(r'<div[^>]*>\s*(<br\s*/?>|\s|&nbsp;)*\s*</div>', re.IGNORECASE)
MULTI_BR = re.compile(r'(<br\s*/?>[\s]*){3,}', re.IGNORECASE)

def clean_post_content(content_html):
    """Clean the inner content of a post (inside .page-content)."""

    # Remove all style attributes from content elements
    # But preserve style on the page-content wrapper itself
    cleaned = content_html

    # Strip inline styles from all tags inside post content
    # Match style="..." on any tag
    def strip_style(match):
        tag = match.group(0)
        # Don't strip from iframe (youtube embeds need it)
        if '<iframe' in tag.lower():
            return tag
        # Don't strip from img src/alt/width/height
        return REMOVE_STYLE_ATTR.sub('', tag)

    # Process all opening tags that have style attributes
    cleaned = re.sub(r'<(?!iframe)[a-z][^>]*style="[^"]*"[^>]*>', strip_style, cleaned, flags=re.IGNORECASE)

    # Remove broken blogspot images (they're all 404)
    cleaned = BROKEN_IMG_PATTERN.sub('', cleaned)

    # Replace broken proxy URLs with empty placeholder
    cleaned = BROKEN_PROXY_PATTERN.sub('', cleaned)

    # Clean excessive <br> tags
    cleaned = MULTI_BR.sub('<br><br>', cleaned)

    # Remove empty divs
    cleaned = EMPTY_DIV.sub('', cleaned)

    # Remove data-insuit-uuid attributes (Blogger cruft)
    cleaned = re.sub(r'\s*data-insuit-uuid="[^"]*"', '', cleaned)

    # Remove imageanchor attributes
    cleaned = re.sub(r'\s*imageanchor="[^"]*"', '', cleaned)

    # Clean up border="0" on images
    cleaned = re.sub(r'\s*border="0"', '', cleaned)

    # Fix links that point to blogspot (convert to simple text if broken)
    # Keep links to external real sites

    return cleaned


def clean_card_image(html_content):
    """Fix post card images - replace broken external URLs with placeholder."""
    def fix_img_src(match):
        full_tag = match.group(0)
        src_match = re.search(r'src="([^"]*)"', full_tag)
        if not src_match:
            return full_tag
        src = src_match.group(1)

        # If it's a broken external URL, remove the src
        if 'lh3.googleusercontent.com' in src or 'bp.blogspot.com' in src:
            # Replace with empty string (CSS will show placeholder)
            return full_tag.replace(f'src="{src}"', 'src="" class="broken-img"')

        return full_tag

    return re.sub(r'<img[^>]*class="post-card-image"[^>]*>', fix_img_src, html_content, flags=re.IGNORECASE)


def fix_generic_titles(html_content):
    """Fix generic titles that just say 'Galeria O+O'."""
    # In post cards, try to extract a better title from the URL
    def fix_card_title(match):
        full_match = match.group(0)
        href_match = re.search(r'href="([^"]*)"', full_match)
        h3_match = re.search(r'<h3>([^<]*)</h3>', full_match)

        if not href_match or not h3_match:
            return full_match

        title = h3_match.group(1).strip()
        href = href_match.group(1)

        # Only fix if title is generic
        if 'Galeria O+O' in title and len(title) < 60:
            # Extract meaningful title from URL
            filename = href.split('/')[-1].replace('.html', '').replace('post-', '')
            # Remove date prefix (YYYY-MM-)
            parts = filename.split('-', 2)
            if len(parts) > 2 and parts[0].isdigit() and parts[1].isdigit():
                meaningful = parts[2]
            else:
                meaningful = filename
            # Convert dashes to spaces and title case
            new_title = meaningful.replace('-', ' ').replace('_', ' ').title()
            if len(new_title) > 3:
                full_match = full_match.replace(f'<h3>{title}</h3>', f'<h3>{new_title}</h3>')

        return full_match

    return re.sub(r'<div class="post-card">.*?</div>\s*</a>\s*</div>', fix_card_title, html_content, flags=re.DOTALL)


def process_post_file(filepath):
    """Process a single post HTML file."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Extract and clean the page-content div
    content_match = re.search(r'(<div class="page-content">)(.*?)(</div>\s*<div class="post-nav">)', content, re.DOTALL)
    if content_match:
        before = content_match.group(1)
        inner = content_match.group(2)
        after = content_match.group(3)

        cleaned_inner = clean_post_content(inner)
        content = content[:content_match.start()] + before + cleaned_inner + after + content[content_match.end():]

    # Fix the h2 title in post
    title_match = re.search(r'<h2[^>]*>Galeria O\+O\s+东西方画廊.*?</h2>', content)
    if title_match:
        # Try to get a better title from the <title> tag
        page_title_match = re.search(r'<title>([^|<]+)', content)
        if page_title_match:
            better_title = page_title_match.group(1).strip()
            if 'Galeria O+O' in better_title:
                # Extract from URL
                filename = os.path.basename(filepath).replace('.html', '').replace('post-', '')
                parts = filename.split('-', 2)
                if len(parts) > 2:
                    better_title = parts[2].replace('-', ' ').replace('_', ' ').title()
            content = content[:title_match.start()] + f'<h2>{better_title}</h2>' + content[title_match.end():]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def process_listing_page(filepath):
    """Process a listing page (index, exposiciones, etc.)."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    content = clean_card_image(content)
    content = fix_generic_titles(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def process_static_page(filepath):
    """Process a static content page (contacta, artistas, etc.)."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Clean page-content sections
    content_match = re.search(r'(<div class="page-content">)(.*?)(</div>\s*</main>)', content, re.DOTALL)
    if content_match:
        before = content_match.group(1)
        inner = content_match.group(2)
        after = content_match.group(3)

        cleaned_inner = clean_post_content(inner)
        content = content[:content_match.start()] + before + cleaned_inner + after + content[content_match.end():]

    # Fix broken external images
    content = BROKEN_IMG_PATTERN.sub('', content)
    content = clean_card_image(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    print("Sanitizing galeriaomaso site...")

    # Process all posts
    posts = list(POSTS_DIR.glob("*.html"))
    print(f"Processing {len(posts)} posts...")
    for i, post in enumerate(posts):
        process_post_file(post)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(posts)} posts processed")
    print(f"  {len(posts)} posts done")

    # Process listing pages
    listing_pages = ['index.html', 'exposiciones.html', 'noticias.html', 'ferias.html', 'internacional.html']
    print(f"Processing {len(listing_pages)} listing pages...")
    for page in listing_pages:
        filepath = SITE_DIR / page
        if filepath.exists():
            process_listing_page(filepath)
            print(f"  {page} done")

    # Process static pages
    static_pages = ['contacta.html', 'artistas.html', 'articulos.html', 'cursos.html', 'enlaces.html', 'como-llegar.html']
    print(f"Processing {len(static_pages)} static pages...")
    for page in static_pages:
        filepath = SITE_DIR / page
        if filepath.exists():
            process_static_page(filepath)
            print(f"  {page} done")

    print("Sanitization complete!")


if __name__ == '__main__':
    main()
