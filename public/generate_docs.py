#!/usr/bin/env python3
"""Generate instruction PDFs in Spanish and English."""

from fpdf import FPDF

class InstructionPDF(FPDF):
    def __init__(self, title):
        super().__init__()
        self.doc_title = title
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(130, 100, 50)
        self.cell(0, 8, self.doc_title, align='R', new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(184, 134, 11)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'{self.page_no()}/{{nb}}', align='C')

    def title_page(self, title, subtitle):
        self.add_page()
        self.ln(40)
        self.set_font('Helvetica', 'B', 26)
        self.set_text_color(44, 36, 32)
        self.multi_cell(0, 12, title, align='C')
        self.ln(6)
        self.set_font('Helvetica', '', 13)
        self.set_text_color(120, 100, 80)
        self.multi_cell(0, 7, subtitle, align='C')
        self.ln(12)
        self.set_draw_color(184, 134, 11)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(8)
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(150, 130, 100)
        self.cell(0, 8, 'Enriqueta Hueso Martinez', align='C')

    def section(self, title):
        self.ln(5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(139, 101, 8)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 170, 100)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(3)

    def subsection(self, title):
        self.ln(2)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(80, 60, 40)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(50, 40, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(1.5)

    def code(self, text):
        self.set_font('Courier', '', 8.5)
        self.set_fill_color(240, 235, 225)
        self.set_text_color(60, 40, 20)
        y = self.get_y()
        h = 6 * (text.count('\n') + 1) + 6
        self.rect(10, y, 190, h, style='F')
        self.set_xy(14, y + 3)
        self.multi_cell(182, 5.5, text)
        self.ln(3)

    def bullet(self, text):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(50, 40, 30)
        self.cell(6, 5.5, '-')
        self.multi_cell(174, 5.5, text)
        self.ln(1)

    def numbered(self, num, text):
        self.set_font('Helvetica', 'B', 9.5)
        self.set_text_color(139, 101, 8)
        self.cell(7, 5.5, f'{num}.')
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(50, 40, 30)
        self.multi_cell(173, 5.5, text)
        self.ln(1)

    def note(self, text):
        self.ln(1)
        self.set_fill_color(255, 248, 230)
        self.set_draw_color(184, 134, 11)
        y = self.get_y()
        h = 5.5 * (text.count('\n') + 1) + 8
        self.rect(10, y, 190, h, style='DF')
        self.set_xy(14, y + 3)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(100, 80, 40)
        self.multi_cell(182, 5.5, text)
        self.ln(3)


def generate_spanish():
    pdf = InstructionPDF('Instrucciones - Enriqueta Hueso Web')
    pdf.alias_nb_pages()
    pdf.title_page('Manual de Instrucciones', 'Sitio Web Enriqueta Hueso Martinez\ny Galeria O+O')

    # 1. Structure
    pdf.add_page()
    pdf.section('1. Estructura del Sitio Web')
    pdf.body('El sitio web tiene dos partes integradas:')
    pdf.bullet('Sitio principal (Enriqueta Hueso): obra, biografia, trayectoria, prensa, contacto, 16 temas visuales, 8 idiomas.')
    pdf.bullet('Galeria O+O: archivo historico con exposiciones, artistas, noticias, ferias, articulos, cursos y contacto.')
    pdf.subsection('Archivos principales')
    pdf.code('index.html              - Pagina principal\ncss/styles.css           - Estilos principales\ncss/themes.css           - 16 temas artisticos\njs/main.js               - Funcionalidad\njs/translations.js       - Traducciones (8 idiomas)\ngallery-data.json        - Datos de la galeria\nbuild_gallery.py         - Herramienta de construccion\nimg/cuadros/             - Carpetas de categorias\ngaleria/                 - Sitio Galeria O+O')

    # 2. Gallery
    pdf.section('2. Gestion de la Galeria de Obra')
    pdf.subsection('Agregar una nueva categoria')
    pdf.numbered(1, 'Crear una carpeta en img/cuadros/ (ej: img/cuadros/Acuarelas/)')
    pdf.numbered(2, 'Colocar imagenes dentro (JPG, JPEG, PNG, BMP, TIFF, GIF, WEBP)')
    pdf.numbered(3, 'Ejecutar: python3 build_gallery.py')
    pdf.numbered(4, 'Refrescar el navegador.')
    pdf.body('El programa detecta automaticamente las imagenes nuevas y las renombra al patron estandar (Categoria_0001.jpeg). Las imagenes existentes NO se tocan.')

    pdf.subsection('Agregar imagenes a una categoria existente')
    pdf.numbered(1, 'Copiar las imagenes nuevas a la carpeta correspondiente')
    pdf.numbered(2, 'Ejecutar: python3 build_gallery.py')
    pdf.body('Las nuevas imagenes se numeran a partir del ultimo numero existente.')

    pdf.subsection('Comando completo')
    pdf.code('python3 build_gallery.py --all')
    pdf.body('Ejecuta todo: escaneo, renombrado automatico, generacion de JSON y miniaturas.')
    pdf.note('NOTA: El programa puede ejecutarse desde cualquier carpeta:\n- enriquetahueso/\n- enriquetahueso/img/\n- enriquetahueso/img/cuadros/\nDetecta automaticamente la raiz del proyecto.')

    pdf.subsection('Estado de venta')
    pdf.body('En gallery-data.json, cada imagen tiene un campo "status":')
    pdf.bullet('"sale" - Disponible para venta')
    pdf.bullet('"sold" - Vendida')
    pdf.bullet('"notforsale" - No disponible')

    # 3. Languages + Themes
    pdf.add_page()
    pdf.section('3. Idiomas y Temas')
    pdf.body('8 idiomas: Espanol, Ingles, Aleman, Frances, Italiano, Chino, Japones, Farsi.')
    pdf.body('16 temas artisticos: Clasico Dorado, Nocturno, Tinta Oriental, Tierra y Ocre, Abstracto Vivo, Blanc i Negre, Historico, Valencia, Vintage, Retro, Swing Jazz, Posmodernista, Picasso, Da Vinci, El Grito, Alto Contraste.')

    # 4. Contact
    pdf.section('4. Formulario de Contacto')
    pdf.body('El formulario intenta abrir el cliente de correo. Si falla, muestra opciones de webmail (Gmail, Outlook, Yahoo). El asunto se rellena automaticamente.')

    # 5. DOMAIN
    pdf.add_page()
    pdf.section('5. Registrar un Dominio')
    pdf.body('Un dominio es la direccion web (ej: enriquetahueso.com). Para registrarlo:')
    pdf.numbered(1, 'Ir a un registrador de dominios. Recomendados:\n   - Namecheap (namecheap.com) - desde 8-10 EUR/ano\n   - Porkbun (porkbun.com) - desde 7-9 EUR/ano\n   - Google Domains (domains.google) - desde 12 EUR/ano')
    pdf.numbered(2, 'Buscar el dominio deseado (ej: enriquetahueso.com)')
    pdf.numbered(3, 'Anadir al carrito y completar la compra')
    pdf.numbered(4, 'Crear una cuenta con email y contrasena')
    pdf.numbered(5, 'Completar el pago (tarjeta o PayPal)')
    pdf.note('CONSEJO: Registrar tambien las variantes .es y .art si estan disponibles.')

    # 6. HOSTING
    pdf.section('6. Contratar Hosting')
    pdf.body('Para un sitio estatico (HTML/CSS/JS) las mejores opciones gratuitas o baratas:')
    pdf.subsection('Opcion A: Netlify (GRATIS - Recomendado)')
    pdf.numbered(1, 'Ir a netlify.com y crear cuenta gratuita')
    pdf.numbered(2, 'Ir a app.netlify.com/drop')
    pdf.numbered(3, 'Arrastrar la carpeta del proyecto completa')
    pdf.numbered(4, 'El sitio estara online en segundos con URL tipo nombre.netlify.app')
    pdf.numbered(5, 'Para actualizaciones: arrastrar de nuevo la carpeta')

    pdf.subsection('Opcion B: GitHub Pages (GRATIS)')
    pdf.numbered(1, 'Crear cuenta en github.com')
    pdf.numbered(2, 'Crear nuevo repositorio (ej: mi-web)')
    pdf.numbered(3, 'Subir todos los archivos al repositorio')
    pdf.numbered(4, 'Ir a Settings > Pages > Source: main branch')
    pdf.numbered(5, 'El sitio estara en usuario.github.io/mi-web')

    pdf.subsection('Opcion C: Hosting tradicional (desde 2-5 EUR/mes)')
    pdf.bullet('Hostinger (hostinger.es) - desde 2 EUR/mes')
    pdf.bullet('SiteGround (siteground.es) - desde 3 EUR/mes')
    pdf.bullet('Ionos (ionos.es) - desde 3 EUR/mes')

    # 7. DNS
    pdf.add_page()
    pdf.section('7. Conectar Dominio al Hosting')
    pdf.subsection('Para Netlify:')
    pdf.numbered(1, 'En Netlify: Site Settings > Domain management > Add domain')
    pdf.numbered(2, 'Escribir el dominio comprado (ej: enriquetahueso.com)')
    pdf.numbered(3, 'Netlify mostrara los servidores DNS (ej: dns1.p01.nsone.net)')
    pdf.numbered(4, 'En el registrador del dominio (Namecheap, etc):')
    pdf.body('   - Ir a la configuracion del dominio\n   - Buscar "Nameservers" o "DNS"\n   - Cambiar a "Custom DNS"\n   - Pegar los nameservers que dio Netlify')
    pdf.numbered(5, 'Esperar 24-48 horas para la propagacion DNS')
    pdf.numbered(6, 'En Netlify: activar HTTPS (SSL gratuito automativo)')

    pdf.subsection('Para GitHub Pages:')
    pdf.numbered(1, 'En GitHub: Settings > Pages > Custom domain > escribir el dominio')
    pdf.numbered(2, 'En el registrador del dominio, anadir registros DNS:')
    pdf.code('Tipo A:     185.199.108.153\nTipo A:     185.199.109.153\nTipo A:     185.199.110.153\nTipo A:     185.199.111.153\nTipo CNAME: www -> usuario.github.io')
    pdf.numbered(3, 'Esperar 24-48 horas')
    pdf.numbered(4, 'Activar "Enforce HTTPS" en GitHub Pages')

    # 8. Upload
    pdf.section('8. Subir el Contenido')
    pdf.subsection('Para Netlify:')
    pdf.body('Simplemente arrastrar la carpeta completa a app.netlify.com/drop cada vez que haya cambios.')
    pdf.subsection('Para hosting tradicional (FTP):')
    pdf.numbered(1, 'Descargar FileZilla (filezilla-project.org) - cliente FTP gratuito')
    pdf.numbered(2, 'Introducir los datos FTP proporcionados por el hosting:\n   - Servidor: ftp.tudominio.com\n   - Usuario y contrasena (del panel de hosting)\n   - Puerto: 21')
    pdf.numbered(3, 'Navegar a la carpeta public_html/ o www/ en el servidor')
    pdf.numbered(4, 'Subir TODOS los archivos del proyecto')
    pdf.note('IMPORTANTE: Subir TODOS los archivos:\n- index.html, css/, js/, img/, gallery-data.json\n- galeria/ (con posts/, images/, style.css, site.js, translations.js)')

    pdf.output('docs/instrucciones_ES.pdf')
    print('Generated: docs/instrucciones_ES.pdf')


def generate_english():
    pdf = InstructionPDF('Instructions - Enriqueta Hueso Web')
    pdf.alias_nb_pages()
    pdf.title_page('Instruction Manual', 'Enriqueta Hueso Martinez Website\nand Gallery O+O')

    # 1. Structure
    pdf.add_page()
    pdf.section('1. Website Structure')
    pdf.body('The website has two integrated parts:')
    pdf.bullet('Main site (Enriqueta Hueso): artwork, biography, career, press, contact, 16 visual themes, 8 languages.')
    pdf.bullet('Gallery O+O: historical archive with exhibitions, artists, news, fairs, articles, courses and contact.')
    pdf.subsection('Main files')
    pdf.code('index.html              - Main page\ncss/styles.css           - Main styles\ncss/themes.css           - 16 artistic themes\njs/main.js               - Functionality\njs/translations.js       - Translations (8 languages)\ngallery-data.json        - Gallery data\nbuild_gallery.py         - Build tool\nimg/cuadros/             - Category folders\ngaleria/                 - Gallery O+O subsite')

    # 2. Gallery
    pdf.section('2. Artwork Gallery Management')
    pdf.subsection('Adding a new category')
    pdf.numbered(1, 'Create a folder in img/cuadros/ (e.g., img/cuadros/Watercolors/)')
    pdf.numbered(2, 'Place images inside (JPG, JPEG, PNG, BMP, TIFF, GIF, WEBP)')
    pdf.numbered(3, 'Run: python3 build_gallery.py')
    pdf.numbered(4, 'Refresh the browser.')
    pdf.body('The tool auto-detects new images and renames them to the standard pattern (Category_0001.jpeg). Existing images are NEVER touched.')

    pdf.subsection('Adding images to an existing category')
    pdf.numbered(1, 'Copy new images to the corresponding folder')
    pdf.numbered(2, 'Run: python3 build_gallery.py')
    pdf.body('New images are numbered starting from the last existing number.')

    pdf.subsection('Full command')
    pdf.code('python3 build_gallery.py --all')
    pdf.body('Runs everything: scan, auto-rename, JSON generation, and thumbnails.')
    pdf.note('NOTE: The tool can be run from any folder:\n- enriquetahueso/\n- enriquetahueso/img/\n- enriquetahueso/img/cuadros/\nIt auto-detects the project root.')

    pdf.subsection('Sale status')
    pdf.body('In gallery-data.json, each image has a "status" field:')
    pdf.bullet('"sale" - Available for purchase')
    pdf.bullet('"sold" - Sold')
    pdf.bullet('"notforsale" - Not available')

    # 3. Languages + Themes
    pdf.add_page()
    pdf.section('3. Languages and Themes')
    pdf.body('8 languages: Spanish, English, German, French, Italian, Chinese, Japanese, Farsi.')
    pdf.body('16 artistic themes: Classic Gold, Nocturne, Oriental Ink, Earth & Ochre, Vivid Abstract, Black & White, Historic, Valencia, Vintage, Retro, Swing Jazz, Postmodernist, Picasso, Da Vinci, The Scream, High Contrast.')

    # 4. Contact
    pdf.section('4. Contact Form')
    pdf.body('The form tries to open the email client. If it fails, it shows webmail options (Gmail, Outlook, Yahoo). The subject auto-fills based on the selected reason.')

    # 5. DOMAIN
    pdf.add_page()
    pdf.section('5. Registering a Domain')
    pdf.body('A domain is your web address (e.g., enriquetahueso.com). To register:')
    pdf.numbered(1, 'Go to a domain registrar. Recommended:\n   - Namecheap (namecheap.com) - from $8-10/year\n   - Porkbun (porkbun.com) - from $7-9/year\n   - Google Domains (domains.google) - from $12/year')
    pdf.numbered(2, 'Search for your desired domain (e.g., enriquetahueso.com)')
    pdf.numbered(3, 'Add to cart and complete the purchase')
    pdf.numbered(4, 'Create an account with email and password')
    pdf.numbered(5, 'Complete payment (credit card or PayPal)')
    pdf.note('TIP: Also register .es and .art variants if available.')

    # 6. HOSTING
    pdf.section('6. Getting Hosting')
    pdf.body('For a static site (HTML/CSS/JS) the best free or cheap options:')
    pdf.subsection('Option A: Netlify (FREE - Recommended)')
    pdf.numbered(1, 'Go to netlify.com and create a free account')
    pdf.numbered(2, 'Go to app.netlify.com/drop')
    pdf.numbered(3, 'Drag your entire project folder onto the page')
    pdf.numbered(4, 'Your site will be online in seconds at name.netlify.app')
    pdf.numbered(5, 'To update: drag the folder again')

    pdf.subsection('Option B: GitHub Pages (FREE)')
    pdf.numbered(1, 'Create account at github.com')
    pdf.numbered(2, 'Create new repository (e.g., my-website)')
    pdf.numbered(3, 'Upload all files to the repository')
    pdf.numbered(4, 'Go to Settings > Pages > Source: main branch')
    pdf.numbered(5, 'Site will be at username.github.io/my-website')

    pdf.subsection('Option C: Traditional hosting (from $2-5/month)')
    pdf.bullet('Hostinger (hostinger.com) - from $2/month')
    pdf.bullet('SiteGround (siteground.com) - from $3/month')
    pdf.bullet('Ionos (ionos.com) - from $3/month')

    # 7. DNS
    pdf.add_page()
    pdf.section('7. Connecting Domain to Hosting')
    pdf.subsection('For Netlify:')
    pdf.numbered(1, 'In Netlify: Site Settings > Domain management > Add domain')
    pdf.numbered(2, 'Type your purchased domain (e.g., enriquetahueso.com)')
    pdf.numbered(3, 'Netlify will show DNS servers (e.g., dns1.p01.nsone.net)')
    pdf.numbered(4, 'In your domain registrar (Namecheap, etc):')
    pdf.body('   - Go to domain settings\n   - Find "Nameservers" or "DNS"\n   - Change to "Custom DNS"\n   - Paste the nameservers from Netlify')
    pdf.numbered(5, 'Wait 24-48 hours for DNS propagation')
    pdf.numbered(6, 'In Netlify: enable HTTPS (automatic free SSL)')

    pdf.subsection('For GitHub Pages:')
    pdf.numbered(1, 'In GitHub: Settings > Pages > Custom domain > type your domain')
    pdf.numbered(2, 'In your domain registrar, add DNS records:')
    pdf.code('Type A:     185.199.108.153\nType A:     185.199.109.153\nType A:     185.199.110.153\nType A:     185.199.111.153\nType CNAME: www -> username.github.io')
    pdf.numbered(3, 'Wait 24-48 hours')
    pdf.numbered(4, 'Enable "Enforce HTTPS" in GitHub Pages')

    # 8. Upload
    pdf.section('8. Uploading Content')
    pdf.subsection('For Netlify:')
    pdf.body('Simply drag the complete folder to app.netlify.com/drop whenever there are changes.')
    pdf.subsection('For traditional hosting (FTP):')
    pdf.numbered(1, 'Download FileZilla (filezilla-project.org) - free FTP client')
    pdf.numbered(2, 'Enter FTP details provided by your hosting:\n   - Server: ftp.yourdomain.com\n   - Username and password (from hosting panel)\n   - Port: 21')
    pdf.numbered(3, 'Navigate to public_html/ or www/ folder on the server')
    pdf.numbered(4, 'Upload ALL project files')
    pdf.note('IMPORTANT: Upload ALL files:\n- index.html, css/, js/, img/, gallery-data.json\n- galeria/ (with posts/, images/, style.css, site.js, translations.js)')

    pdf.output('docs/instructions_EN.pdf')
    print('Generated: docs/instructions_EN.pdf')


if __name__ == '__main__':
    import os
    os.makedirs('docs', exist_ok=True)
    generate_spanish()
    generate_english()
    print('\nBoth PDFs generated in docs/ folder.')
