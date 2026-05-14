#!/usr/bin/env python3
"""
Gallery Builder for Enriqueta Hueso Website
============================================
Scans img/cuadros/ for category folders and images.
Automatically renames NEW images to the standard pattern.
Generates gallery-data.json for the website.

Usage:
    python3 build_gallery.py              # Scan, auto-rename, generate JSON
    python3 build_gallery.py --all        # Same + generate thumbnails
    python3 build_gallery.py --thumbs     # Also generate thumbnails (requires Pillow)

Can be run from anywhere:
    - enriquetahueso/
    - enriquetahueso/img/
    - enriquetahueso/img/cuadros/
    - or any other location (auto-detects project root)

How auto-rename works:
    - Images matching <CategoryName>_NNNN.<ext> are KEPT as-is
    - Any OTHER image file is considered NEW and gets renamed
    - New images are numbered starting from the last existing number + 1
    - Original extension is preserved (jpg, jpeg, png, bmp, tiff, gif, webp)
"""

import os
import sys
import re
import json
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
THUMB_SIZE = (600, 600)

ROMAN = ['I','II','III','IV','V','VI','VII','VIII','IX','X',
         'XI','XII','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX',
         'XXI','XXII','XXIII','XXIV','XXV','XXVI','XXVII','XXVIII','XXIX','XXX',
         'XXXI','XXXII','XXXIII','XXXIV','XXXV','XXXVI','XXXVII','XXXVIII','XXXIX','XL',
         'XLI','XLII','XLIII','XLIV','XLV','XLVI','XLVII','XLVIII','XLIX','L']

CATEGORY_NAMES = {
    'Pinturas': 'Pinturas',
    'Collage': 'Collage',
    'Grabado': 'Grabado',
    'Tintas': 'Tintas',
    'Tintas_y_collage': 'Tintas y Collage',
}

CATEGORY_PREFIX = {
    'Pinturas': 'P',
    'Collage': 'C',
    'Grabado': 'G',
    'Tintas': 'T',
    'Tintas_y_collage': 'TC',
}


# =============================================================
# Auto-detect project root
# =============================================================
def find_project_root():
    """
    Find the project root (the folder containing index.html + img/cuadros/).
    Searches from multiple starting points:
      1. The directory where this script lives
      2. The current working directory
      3. Walk up from cwd looking for the project structure
    """
    candidates = []

    # 1. Script's own directory
    script_dir = Path(__file__).resolve().parent
    candidates.append(script_dir)

    # 2. Current working directory
    cwd = Path.cwd().resolve()
    candidates.append(cwd)

    # 3. Walk up from cwd (handles running from img/ or img/cuadros/)
    p = cwd
    while p != p.parent:
        candidates.append(p)
        p = p.parent

    # Check each candidate
    for candidate in candidates:
        cuadros = candidate / "img" / "cuadros"
        if cuadros.is_dir():
            return candidate

    # Last resort: if cwd IS the cuadros folder
    if cwd.name == 'cuadros' and cwd.is_dir():
        return cwd.parent.parent

    # Or if cwd is the img folder
    if cwd.name == 'img' and (cwd / 'cuadros').is_dir():
        return cwd.parent

    return None


def get_paths():
    """Get all paths relative to the auto-detected project root."""
    root = find_project_root()
    if root is None:
        print("ERROR: Could not find project root.")
        print("  Looking for a folder containing img/cuadros/")
        print("  Run from the project directory or pass the path.")
        sys.exit(1)

    cuadros = root / "img" / "cuadros"
    output_json = root / "gallery-data.json"
    thumb_dir = root / "img" / "cuadros_thumbs"

    return root, cuadros, output_json, thumb_dir


# =============================================================
# Helpers
# =============================================================
def get_display_name(folder_name):
    if folder_name in CATEGORY_NAMES:
        return CATEGORY_NAMES[folder_name]
    return folder_name.replace('_', ' ')


def get_filter_id(folder_name):
    return folder_name.lower().replace(' ', '_')


def get_prefix(folder_name):
    if folder_name in CATEGORY_PREFIX:
        return CATEGORY_PREFIX[folder_name]
    words = folder_name.replace('_', ' ').split()
    if len(words) == 1:
        return words[0][:2].upper()
    return ''.join(w[0].upper() for w in words)


def is_standard_name(filename, folder_name):
    pattern = re.compile(rf'^{re.escape(folder_name)}_(\d{{4}})\.\w+$', re.IGNORECASE)
    return pattern.match(filename)


def get_number_from_name(filename, folder_name):
    match = re.match(rf'^{re.escape(folder_name)}_(\d{{4}})\.\w+$', filename, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def is_image(filepath):
    return filepath.suffix.lower() in IMAGE_EXTENSIONS


# =============================================================
# Auto-rename
# =============================================================
def auto_rename_new_images(folder):
    folder_name = folder.name
    all_images = [f for f in sorted(folder.iterdir()) if f.is_file() and is_image(f)]
    if not all_images:
        return 0

    existing = []
    new_files = []
    for img in all_images:
        if is_standard_name(img.name, folder_name):
            existing.append(img)
        else:
            new_files.append(img)

    if not new_files:
        return 0

    max_number = max((get_number_from_name(img.name, folder_name) for img in existing), default=0)
    next_number = max_number + 1
    renamed = 0

    for img in new_files:
        ext = img.suffix.lower()
        new_name = f"{folder_name}_{next_number:04d}{ext}"
        new_path = folder / new_name

        while new_path.exists():
            next_number += 1
            new_name = f"{folder_name}_{next_number:04d}{ext}"
            new_path = folder / new_name

        img.rename(new_path)
        print(f"    Renamed: {img.name} -> {new_name}")
        renamed += 1
        next_number += 1

    return renamed


# =============================================================
# Scan & Build
# =============================================================
def scan_and_build(cuadros_dir):
    categories = []
    total_renamed = 0

    for folder in sorted(cuadros_dir.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue

        renamed = auto_rename_new_images(folder)
        total_renamed += renamed

        images = sorted([f.name for f in folder.iterdir() if f.is_file() and is_image(f)])
        if not images:
            print(f"  Skipping {folder.name}: no images found")
            continue

        display_name = get_display_name(folder.name)
        filter_id = get_filter_id(folder.name)
        prefix = get_prefix(folder.name)

        category = {
            'folder': folder.name,
            'display_name': display_name,
            'filter_id': filter_id,
            'prefix': prefix,
            'images': []
        }

        for i, img_name in enumerate(images, 1):
            roman = ROMAN[i-1] if i <= len(ROMAN) else str(i)
            category['images'].append({
                'file': img_name,
                'path': f"img/cuadros/{folder.name}/{img_name}",
                'title': f"{display_name} {roman}",
                'ref': f"EH-{prefix}-{i:03d}",
                'status': 'sale',
            })

        categories.append(category)
        status = f" ({renamed} new renamed)" if renamed else ""
        print(f"  {folder.name}: {len(images)} images -> {display_name}{status}")

    return categories, total_renamed


# =============================================================
# Thumbnails
# =============================================================
def generate_thumbnails(categories, cuadros_dir, thumb_dir):
    try:
        from PIL import Image
    except ImportError:
        print("  WARNING: Pillow not installed. Run: pip install Pillow")
        print("  Skipping thumbnail generation.")
        return

    thumb_dir.mkdir(parents=True, exist_ok=True)
    generated = 0

    for cat in categories:
        cat_thumb_dir = thumb_dir / cat['folder']
        cat_thumb_dir.mkdir(exist_ok=True)

        for img in cat['images']:
            src = cuadros_dir / cat['folder'] / img['file']
            thumb_name = Path(img['file']).stem + '.jpeg'
            dst = cat_thumb_dir / thumb_name

            if dst.exists():
                continue

            try:
                with Image.open(src) as im:
                    im.thumbnail(THUMB_SIZE, Image.LANCZOS)
                    if im.mode in ('RGBA', 'P', 'LA'):
                        im = im.convert('RGB')
                    im.save(dst, 'JPEG', quality=85)
                    print(f"    Thumbnail: {img['file']} -> {thumb_name}")
                    generated += 1
            except Exception as e:
                print(f"    ERROR: {img['file']}: {e}")
                shutil.copy2(src, dst)

    print(f"  {generated} thumbnails generated")


# =============================================================
# JSON output
# =============================================================
def write_json(categories, output_json):
    existing_status = {}
    if output_json.exists():
        try:
            with open(output_json, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            for cat in old_data.get('categories', []):
                for img in cat.get('images', []):
                    existing_status[img['path']] = img.get('status', 'sale')
        except (json.JSONDecodeError, KeyError):
            pass

    for cat in categories:
        for img in cat['images']:
            if img['path'] in existing_status:
                img['status'] = existing_status[img['path']]

    data = {
        '_comment': 'Auto-generated by build_gallery.py. Edit status values only.',
        '_usage': 'Run: python3 build_gallery.py --all',
        '_status_values': 'sale | sold | notforsale',
        'categories': categories
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total = sum(len(c['images']) for c in categories)
    print(f"\n  Written: {output_json}")
    print(f"  {len(categories)} categories, {total} total images")


# =============================================================
# Main
# =============================================================
def main():
    do_all = '--all' in sys.argv
    do_thumbs = '--thumbs' in sys.argv or do_all

    print("=" * 55)
    print("  Gallery Builder - Enriqueta Hueso")
    print("=" * 55)

    root, cuadros_dir, output_json, thumb_dir = get_paths()

    print(f"\n  Project root: {root}")
    print(f"  Cuadros dir:  {cuadros_dir}")
    print(f"  Output JSON:  {output_json}")
    print(f"\n  Auto-renaming new images...\n")

    categories, total_renamed = scan_and_build(cuadros_dir)

    if not categories:
        print("No categories found!")
        sys.exit(1)

    if total_renamed > 0:
        print(f"\n  Auto-renamed {total_renamed} new image(s)")

    if do_thumbs:
        print("\nGenerating thumbnails...")
        generate_thumbnails(categories, cuadros_dir, thumb_dir)

    print("\nGenerating gallery-data.json...")
    write_json(categories, output_json)

    print("\nDone! Refresh the browser to see changes.")


if __name__ == '__main__':
    main()
