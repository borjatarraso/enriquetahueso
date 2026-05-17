"""Inject ArtGallery (LocalBusiness) JSON-LD into pages where it makes sense.

Targets: site/contacta.html, site/como-llegar.html, site/index.html.
Idempotent via LOCAL-BUSINESS marker. Mirrors to both site/ and public/site/.
"""
import json
import re
from pathlib import Path

REPO = Path("/home/overdrive/claude/enriquetahueso")
ROOTS = [REPO / "site", REPO / "public" / "site"]
SITE_URL = "https://enriquetahueso.com"
MARKER = "<!-- LOCAL-BUSINESS-JSONLD -->"

TARGETS = {"contacta", "como-llegar", "index"}

# Approximate coordinates intentionally omitted; let Google geocode from
# the postal address. Adding inaccurate coords actively hurts local SERP.
BUSINESS = {
    "@context": "https://schema.org",
    "@type": ["ArtGallery", "LocalBusiness"],
    "@id": SITE_URL + "/site/#galleryoo",
    "name": "Galería O+O",
    "alternateName": ["东西方画廊", "Galería O+O (Oriente y Occidente)"],
    "description": (
        "Galería O+O (东西方画廊) — espacio de referencia internacional de "
        "arte entre Oriente y Occidente, fundado en Valencia por la artista "
        "Enriqueta Hueso Martínez."
    ),
    "url": SITE_URL + "/site/",
    "image": SITE_URL + "/img/brand/og-image.jpg",
    "logo": SITE_URL + "/img/brand/favicon-512.png",
    "telephone": ["+34 961 33 64 49", "+34 639 99 03 92"],
    "email": "enriqueta.hueso@gmail.com",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "C/ Francisco Martínez 34-36 Bajo",
        "addressLocality": "Valencia",
        "addressRegion": "Comunidad Valenciana",
        "postalCode": "46020",
        "addressCountry": "ES",
    },
    "openingHoursSpecification": [
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "17:30",
            "closes": "20:30",
        },
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": "Saturday",
            "opens": "11:30",
            "closes": "13:30",
        },
    ],
    "founder": {
        "@type": "Person",
        "@id": SITE_URL + "/#person",
        "name": "Enriqueta Hueso Martínez",
        "url": SITE_URL + "/",
    },
    "areaServed": ["España", "China", "Japón", "Internacional"],
    "knowsLanguage": ["es", "en", "zh", "ja"],
    "priceRange": "€€",
}


def inject(file_path: Path) -> bool:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    if MARKER in text:
        return False
    if file_path.stem not in TARGETS:
        return False
    jsonld = json.dumps(BUSINESS, ensure_ascii=False, indent=2)
    block = (
        f"    {MARKER}\n"
        f'    <script type="application/ld+json">\n{jsonld}\n    </script>\n'
    )
    new_text, n = re.subn(
        r"</head>", block + "</head>", text, count=1, flags=re.IGNORECASE
    )
    if n == 0:
        return False
    file_path.write_text(new_text, encoding="utf-8")
    return True


def main():
    total = 0
    for root in ROOTS:
        if not root.exists():
            continue
        for p in root.glob("*.html"):
            if inject(p):
                total += 1
                print(f"  + {p}")
    print(f"Injected LocalBusiness JSON-LD into {total} files.")


if __name__ == "__main__":
    main()
