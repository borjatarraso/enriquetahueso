"""Generate og-image + favicon set for enriquetahueso.com.

Outputs to public/img/brand/ (og-image, EH monogram favicons in multiple sizes).
Re-runnable: overwrites existing files.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = Path("/home/overdrive/claude/enriquetahueso/public/img/brand")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SERIF_BOLD = "/usr/share/fonts/google-noto-vf/NotoSerif[wght].ttf"
SERIF_REGULAR = "/usr/share/fonts/google-noto-vf/NotoSerif[wght].ttf"
SERIF_ITALIC = "/usr/share/fonts/google-noto-vf/NotoSerif-Italic[wght].ttf"

# Warm dark palette (nocturne theme)
BG_TOP = (24, 18, 14)
BG_BOTTOM = (44, 28, 18)
GOLD = (212, 175, 86)
GOLD_DIM = (170, 132, 60)
CREAM = (242, 230, 208)


def gradient_bg(size, top, bottom):
    w, h = size
    base = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return base


def soft_circle(size, color, blur=40, alpha=140):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = size
    pad = min(w, h) // 6
    d.ellipse([pad, pad, w - pad, h - pad], fill=(*color, alpha))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def build_og_image():
    """1200x630 social card."""
    W, H = 1200, 630
    img = gradient_bg((W, H), BG_TOP, BG_BOTTOM).convert("RGBA")

    # Soft warm glow off-center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([-100, 200, 500, 800], fill=(*GOLD_DIM, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img.alpha_composite(glow)

    # Right-side accent stripe (brush mark)
    stripe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = ImageDraw.Draw(stripe)
    s.rectangle([W - 12, 0, W - 4, H], fill=(*GOLD, 200))
    img.alpha_composite(stripe)

    draw = ImageDraw.Draw(img)

    # Pre-title (small caps, gold)
    pre_font = ImageFont.truetype(SERIF_REGULAR, 28)
    draw.text((80, 130), "ARTISTA  ·  GALERISTA  ·  GESTORA CULTURAL",
              font=pre_font, fill=GOLD)

    # Main name (large serif, cream)
    name_font = ImageFont.truetype(SERIF_BOLD, 92)
    draw.text((76, 180), "Enriqueta", font=name_font, fill=CREAM)
    draw.text((76, 280), "Hueso Martínez", font=name_font, fill=CREAM)

    # Underline accent
    draw.rectangle([80, 398, 320, 402], fill=GOLD)

    # Tagline (italic)
    tag_font = ImageFont.truetype(SERIF_ITALIC, 30)
    draw.text((80, 430),
              "«Mi pintura es un lenguaje de signos",
              font=tag_font, fill=CREAM)
    draw.text((80, 470),
              "que prefiero sentir antes que explicar».",
              font=tag_font, fill=CREAM)

    # Domain at bottom
    dom_font = ImageFont.truetype(SERIF_REGULAR, 26)
    draw.text((80, 555), "enriquetahueso.com", font=dom_font, fill=GOLD)

    # Valencia mark, right side
    loc_font = ImageFont.truetype(SERIF_ITALIC, 24)
    txt = "Valencia · España"
    bbox = draw.textbbox((0, 0), txt, font=loc_font)
    tw = bbox[2] - bbox[0]
    draw.text((W - tw - 80, 558), txt, font=loc_font, fill=CREAM)

    out = img.convert("RGB")
    out.save(OUT_DIR / "og-image.jpg", "JPEG", quality=88, optimize=True, progressive=True)
    print(f"og-image.jpg → {(OUT_DIR / 'og-image.jpg').stat().st_size // 1024} KB")


def build_monogram(size_px, with_bg=True, padded=True):
    """Square EH monogram. Returns RGBA Image."""
    s = size_px
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if with_bg:
        # Rounded square bg
        radius = s // 6
        bg_layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bg_layer)
        # gradient fill via two-tone
        bd.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=BG_BOTTOM)
        img.alpha_composite(bg_layer)

    # Choose font size proportional to canvas
    font_px = int(s * (0.62 if padded else 0.82))
    try:
        font = ImageFont.truetype(SERIF_BOLD, font_px)
    except OSError:
        font = ImageFont.load_default()

    text = "EH"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (s - tw) // 2 - bbox[0]
    y = (s - th) // 2 - bbox[1] - int(s * 0.02)
    draw.text((x, y), text, font=font, fill=GOLD)
    return img


def build_favicons():
    # PNG favicons (modern browsers / PWA)
    for size in (16, 32, 48, 192, 512):
        img = build_monogram(size, with_bg=(size >= 32))
        img.save(OUT_DIR / f"favicon-{size}.png", "PNG", optimize=True)

    # Apple touch icon (180x180, no transparency, rounded handled by iOS)
    apple = build_monogram(180, with_bg=True)
    apple.convert("RGB").save(OUT_DIR / "apple-touch-icon.png", "PNG", optimize=True)

    # Multi-resolution .ico (16, 32, 48)
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    ico_imgs = [build_monogram(s).convert("RGBA") for s, _ in ico_sizes]
    ico_imgs[0].save(OUT_DIR / "favicon.ico", format="ICO",
                     sizes=ico_sizes, append_images=ico_imgs[1:])

    # SVG monogram (scalable, used as primary <link rel="icon" type="image/svg+xml">)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="rgb{BG_BOTTOM}"/>
  <text x="32" y="44" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-weight="700" font-size="36" fill="rgb{GOLD}">EH</text>
</svg>
"""
    (OUT_DIR / "favicon.svg").write_text(svg)

    for f in sorted(OUT_DIR.glob("favicon*")):
        print(f"{f.name} → {f.stat().st_size} B")
    apple_p = OUT_DIR / "apple-touch-icon.png"
    print(f"{apple_p.name} → {apple_p.stat().st_size} B")


if __name__ == "__main__":
    build_og_image()
    build_favicons()
    print("\nAll brand assets written to:", OUT_DIR)
