/**
 * Enriqueta Hueso Martínez - Personal Website
 * Main JavaScript - with Theme, View, Language controls
 */

(function () {
    'use strict';

    // ============================================================
    // Loader
    // ============================================================
    window.addEventListener('load', function () {
        setTimeout(function () {
            document.getElementById('loader').classList.add('loaded');
        }, 800);
    });

    // Current year
    document.getElementById('currentYear').textContent = new Date().getFullYear();

    // ============================================================
    // Hero Canvas (generative art)
    // ============================================================
    function initHeroCanvas() {
        var container = document.getElementById('heroCanvas');
        if (!container) return;

        var canvas = document.createElement('canvas');
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        container.appendChild(canvas);

        var ctx = canvas.getContext('2d');
        var w, h;
        var particles = [];
        var shapes = [];

        function resize() {
            w = canvas.width = container.offsetWidth;
            h = canvas.height = container.offsetHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        var colors = [
            'rgba(184, 134, 11, 0.3)', 'rgba(196, 98, 58, 0.25)',
            'rgba(61, 79, 124, 0.2)', 'rgba(107, 127, 94, 0.2)',
            'rgba(204, 136, 51, 0.15)', 'rgba(212, 168, 67, 0.2)'
        ];

        for (var i = 0; i < 8; i++) {
            shapes.push({
                x: Math.random() * w, y: Math.random() * h,
                radius: 50 + Math.random() * 200,
                color: colors[i % colors.length],
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                phase: Math.random() * Math.PI * 2
            });
        }

        for (var j = 0; j < 40; j++) {
            particles.push({
                x: Math.random() * w, y: Math.random() * h,
                size: 1 + Math.random() * 3,
                color: colors[Math.floor(Math.random() * colors.length)],
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                life: Math.random()
            });
        }

        var time = 0;

        function draw() {
            ctx.clearRect(0, 0, w, h);
            time += 0.005;

            for (var s = 0; s < shapes.length; s++) {
                var shape = shapes[s];
                shape.x += shape.vx + Math.sin(time + shape.phase) * 0.2;
                shape.y += shape.vy + Math.cos(time + shape.phase) * 0.2;
                if (shape.x < -shape.radius) shape.x = w + shape.radius;
                if (shape.x > w + shape.radius) shape.x = -shape.radius;
                if (shape.y < -shape.radius) shape.y = h + shape.radius;
                if (shape.y > h + shape.radius) shape.y = -shape.radius;

                ctx.beginPath();
                var gradient = ctx.createRadialGradient(shape.x, shape.y, 0, shape.x, shape.y, shape.radius);
                gradient.addColorStop(0, shape.color);
                gradient.addColorStop(1, 'transparent');
                ctx.fillStyle = gradient;
                ctx.arc(shape.x, shape.y, shape.radius, 0, Math.PI * 2);
                ctx.fill();
            }

            // Concentric circles
            var cx = w * 0.65, cy = h * 0.45;
            for (var r = 0; r < 5; r++) {
                ctx.beginPath();
                ctx.arc(cx, cy, 30 + r * 40 + Math.sin(time * 2 + r) * 10, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(184, 134, 11, ' + (0.08 - r * 0.012) + ')';
                ctx.lineWidth = 1;
                ctx.stroke();
            }

            // Spiral
            ctx.beginPath();
            var sx = w * 0.3, sy = h * 0.6;
            for (var a = 0; a < Math.PI * 6; a += 0.1) {
                var sr = a * 5 + Math.sin(time) * 3;
                var px = sx + sr * Math.cos(a + time * 0.3);
                var py = sy + sr * Math.sin(a + time * 0.3);
                if (a === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
            }
            ctx.strokeStyle = 'rgba(196, 98, 58, 0.06)';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // Particles
            for (var p = 0; p < particles.length; p++) {
                var part = particles[p];
                part.x += part.vx; part.y += part.vy; part.life += 0.002;
                if (part.x < 0) part.x = w; if (part.x > w) part.x = 0;
                if (part.y < 0) part.y = h; if (part.y > h) part.y = 0;
                ctx.beginPath();
                ctx.arc(part.x, part.y, part.size, 0, Math.PI * 2);
                ctx.fillStyle = part.color.replace(/[\d.]+\)$/, (0.2 + Math.sin(part.life * Math.PI) * 0.3) + ')');
                ctx.fill();
            }

            requestAnimationFrame(draw);
        }
        draw();
    }
    initHeroCanvas();

    // ============================================================
    // Navigation
    // ============================================================
    var nav = document.getElementById('mainNav');
    var hamburger = document.getElementById('navHamburger');
    var navLinks = document.getElementById('navLinks');
    var navAnchors = navLinks.querySelectorAll('a');

    window.addEventListener('scroll', function () {
        var scrollY = window.pageYOffset || document.documentElement.scrollTop;
        if (scrollY > 80) nav.classList.add('scrolled');
        else nav.classList.remove('scrolled');
        updateActiveNav();
    });

    hamburger.addEventListener('click', function () {
        hamburger.classList.toggle('open');
        navLinks.classList.toggle('open');
        document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
    });

    for (var i = 0; i < navAnchors.length; i++) {
        navAnchors[i].addEventListener('click', function () {
            hamburger.classList.remove('open');
            navLinks.classList.remove('open');
            document.body.style.overflow = '';
        });
    }

    function updateActiveNav() {
        var sections = document.querySelectorAll('section[id], header[id]');
        var scrollPos = window.pageYOffset + 150;
        for (var s = 0; s < sections.length; s++) {
            var section = sections[s];
            if (scrollPos >= section.offsetTop && scrollPos < section.offsetTop + section.offsetHeight) {
                var id = section.id;
                for (var a = 0; a < navAnchors.length; a++) {
                    navAnchors[a].classList.remove('active');
                    if (navAnchors[a].getAttribute('href') === '#' + id) {
                        navAnchors[a].classList.add('active');
                    }
                }
            }
        }
    }

    // ============================================================
    // Dropdown helper - close all dropdowns on outside click
    // ============================================================
    var allDropdowns = document.querySelectorAll('.toolbar-dropdown');

    function closeAllDropdowns() {
        for (var d = 0; d < allDropdowns.length; d++) {
            allDropdowns[d].classList.remove('open');
        }
    }

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.toolbar-group')) {
            closeAllDropdowns();
        }
    });

    function toggleDropdown(dropdown, e) {
        e.stopPropagation();
        var wasOpen = dropdown.classList.contains('open');
        closeAllDropdowns();
        if (!wasOpen) dropdown.classList.add('open');
    }

    // ============================================================
    // Language Selector
    // ============================================================
    var langToggle = document.getElementById('langToggle');
    var langDropdown = document.getElementById('langDropdown');
    var langOptions = langDropdown.querySelectorAll('.dropdown-option');
    var langLabel = document.getElementById('langLabel');
    var langFlag = document.getElementById('langFlag');
    var currentLang = 'es';

    var langLabels = {
        es: 'ES', en: 'EN', de: 'DE', fr: 'FR',
        it: 'IT', zh: '中', ja: '日', fa: 'فا'
    };
    var langFlags = {
        es: '\uD83C\uDDEA\uD83C\uDDF8',
        en: '\uD83C\uDDEC\uD83C\uDDE7',
        de: '\uD83C\uDDE9\uD83C\uDDEA',
        fr: '\uD83C\uDDEB\uD83C\uDDF7',
        it: '\uD83C\uDDEE\uD83C\uDDF9',
        zh: '\uD83C\uDDE8\uD83C\uDDF3',
        ja: '\uD83C\uDDEF\uD83C\uDDF5',
        fa: '\uD83C\uDDEE\uD83C\uDDF7'
    };
    var rtlLanguages = ['fa'];

    langToggle.addEventListener('click', function (e) {
        toggleDropdown(langDropdown, e);
    });

    for (var l = 0; l < langOptions.length; l++) {
        langOptions[l].addEventListener('click', function (e) {
            e.stopPropagation();
            switchLanguage(this.getAttribute('data-lang'));
            closeAllDropdowns();
        });
    }

    // Google Translate language codes (Chinese needs zh-CN; rest match).
    var gtLangMap = { es: 'es', en: 'en', de: 'de', fr: 'fr', it: 'it', zh: 'zh-CN', ja: 'ja', fa: 'fa' };

    function setGoogTransCookie(value) {
        var host = location.hostname.replace(/^www\./, '');
        if (value === null) {
            // Clear: expire on all relevant scopes.
            document.cookie = 'googtrans=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
            if (host && host.indexOf('.') !== -1) {
                document.cookie = 'googtrans=; path=/; domain=.' + host + '; expires=Thu, 01 Jan 1970 00:00:00 GMT';
            }
            return;
        }
        document.cookie = 'googtrans=' + value + '; path=/; max-age=' + (86400 * 365);
        if (host && host.indexOf('.') !== -1) {
            document.cookie = 'googtrans=' + value + '; path=/; domain=.' + host + '; max-age=' + (86400 * 365);
        }
    }

    function switchLanguage(lang, skipReload) {
        if (!translations[lang]) return;
        var prevLang = currentLang;
        currentLang = lang;

        for (var o = 0; o < langOptions.length; o++) {
            langOptions[o].classList.remove('active');
            if (langOptions[o].getAttribute('data-lang') === lang) langOptions[o].classList.add('active');
        }

        langLabel.textContent = langLabels[lang];
        // For Farsi, use the Pahlavi SVG flag (don't replace innerHTML)
        if (lang === 'fa') {
            langFlag.innerHTML = '<svg viewBox="0 0 36 24" width="18" height="12"><rect width="36" height="8" fill="#239f40"/><rect y="8" width="36" height="8" fill="#fff"/><rect y="16" width="36" height="8" fill="#da0000"/><circle cx="18" cy="12" r="3.5" fill="#da0000"/><path d="M15.5 10.5c0 0 1-1.5 2.5-1.5s2.5 1.5 2.5 1.5" stroke="#f4c430" stroke-width="0.6" fill="none"/><line x1="18" y1="8" x2="18" y2="10" stroke="#f4c430" stroke-width="0.7"/><line x1="16.5" y1="9" x2="17.5" y2="10.5" stroke="#f4c430" stroke-width="0.5"/><line x1="19.5" y1="9" x2="18.5" y2="10.5" stroke="#f4c430" stroke-width="0.5"/></svg>';
        } else {
            langFlag.textContent = langFlags[lang];
        }
        document.documentElement.lang = lang;
        document.documentElement.dir = rtlLanguages.indexOf(lang) !== -1 ? 'rtl' : 'ltr';

        // Apply curated translations for the elements that have them — snappy
        // and high-quality for the artist's own phrasing.
        var elements = document.querySelectorAll('[data-i18n]');
        for (var e = 0; e < elements.length; e++) {
            var key = elements[e].getAttribute('data-i18n');
            if (translations[lang][key]) {
                if (elements[e].tagName === 'INPUT' || elements[e].tagName === 'TEXTAREA') {
                    elements[e].placeholder = translations[lang][key];
                } else {
                    elements[e].textContent = translations[lang][key];
                }
            }
        }

        // Persist choice across reloads.
        try { localStorage.setItem('eh-lang', lang); } catch(err) {}

        // Drive Google Translate for everything the dictionary doesn't cover
        // (gallery cards, address blocks, alt text, dynamic form text…).
        // Cookie + soft reload is the most reliable trigger across browsers;
        // the head pre-init script applies the cookie before GT loads so the
        // post-reload paint comes up already translated, no Spanish flash.
        if (skipReload || lang === prevLang) return;
        if (lang === 'es') {
            setGoogTransCookie(null);
        } else {
            setGoogTransCookie('/es/' + (gtLangMap[lang] || lang));
        }
        location.reload();
    }

    // Restore saved language on page load: refresh dropdown UI and apply the
    // curated dictionary, but skip the reload (we just landed — Google
    // Translate is already painting the rest based on the cookie set in <head>).
    try {
        var savedLang = localStorage.getItem('eh-lang');
        if (savedLang && translations[savedLang]) switchLanguage(savedLang, true);
    } catch(e) {}

    // ============================================================
    // Theme Selector
    // ============================================================
    var themeToggle = document.getElementById('themeToggle');
    var themeDropdown = document.getElementById('themeDropdown');
    var themeOptions = themeDropdown.querySelectorAll('.dropdown-option');
    var themeLabel = document.getElementById('themeLabel');

    themeToggle.addEventListener('click', function (e) {
        toggleDropdown(themeDropdown, e);
    });

    for (var t = 0; t < themeOptions.length; t++) {
        themeOptions[t].addEventListener('click', function (e) {
            e.stopPropagation();
            var theme = this.getAttribute('data-theme');
            switchTheme(theme);
            closeAllDropdowns();
        });
    }

    function switchTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);

        for (var o = 0; o < themeOptions.length; o++) {
            themeOptions[o].classList.remove('active');
            if (themeOptions[o].getAttribute('data-theme') === theme) {
                themeOptions[o].classList.add('active');
                // Update label with translated name
                var i18nKey = themeOptions[o].getAttribute('data-i18n');
                if (translations[currentLang] && translations[currentLang][i18nKey]) {
                    themeLabel.textContent = translations[currentLang][i18nKey];
                } else {
                    themeLabel.textContent = themeOptions[o].textContent;
                }
            }
        }

        try { localStorage.setItem('eh-theme', theme); } catch(e) {}
    }

    // Restore saved theme, default to Nocturno for first-time visitors.
    try {
        var savedTheme = localStorage.getItem('eh-theme');
        switchTheme(savedTheme || 'nocturne');
    } catch(e) { switchTheme('nocturne'); }

    // ============================================================
    // View Mode Toggle (Desktop / Mobile)
    // ============================================================
    var viewToggle = document.getElementById('viewToggle');
    var viewLabel = document.getElementById('viewLabel');
    var viewIconDesktop = viewToggle.querySelector('.view-icon-desktop');
    var viewIconMobile = viewToggle.querySelector('.view-icon-mobile');
    var currentView = 'auto'; // auto, mobile, desktop

    function detectView() {
        var isMobile = window.innerWidth <= 768;
        return isMobile ? 'mobile' : 'desktop';
    }

    function updateViewUI() {
        var effectiveView = currentView === 'auto' ? detectView() : currentView;
        var isMobileView = effectiveView === 'mobile';

        if (isMobileView) {
            viewIconDesktop.style.display = 'none';
            viewIconMobile.style.display = 'block';
            if (translations[currentLang] && translations[currentLang]['toolbar.mobile']) {
                viewLabel.textContent = translations[currentLang]['toolbar.mobile'];
            } else {
                viewLabel.textContent = 'Móvil';
            }
        } else {
            viewIconDesktop.style.display = 'block';
            viewIconMobile.style.display = 'none';
            if (translations[currentLang] && translations[currentLang]['toolbar.desktop']) {
                viewLabel.textContent = translations[currentLang]['toolbar.desktop'];
            } else {
                viewLabel.textContent = 'Escritorio';
            }
        }

        // Set data-view attribute
        document.documentElement.setAttribute('data-view', currentView);
    }

    viewToggle.addEventListener('click', function () {
        if (currentView === 'auto') {
            // If auto (which shows current device), toggle to the opposite
            currentView = detectView() === 'desktop' ? 'mobile' : 'desktop';
        } else if (currentView === 'mobile') {
            currentView = 'desktop';
        } else {
            currentView = 'mobile';
        }
        updateViewUI();
    });

    updateViewUI();

    // Update on resize if auto
    window.addEventListener('resize', function () {
        if (currentView === 'auto') updateViewUI();
    });

    // ============================================================
    // Dynamic Gallery - loads from gallery-data.json
    // ============================================================
    var obraFilters = document.getElementById('obraFilters');
    var obraGrid = document.getElementById('obraGrid');
    var filterBtns, obraItems;

    function buildGallery(data) {
        if (!obraFilters || !obraGrid || !data || !data.categories) return;

        // Build filter buttons
        var filtersHtml = '<button class="filter-btn active" data-filter="all" data-i18n="obra.all">Todas</button>';
        for (var c = 0; c < data.categories.length; c++) {
            var cat = data.categories[c];
            filtersHtml += '<button class="filter-btn" data-filter="' + cat.filter_id + '">' + cat.display_name + '</button>';
        }
        obraFilters.innerHTML = filtersHtml;

        // Build grid
        var gridHtml = '';
        for (var c = 0; c < data.categories.length; c++) {
            var cat = data.categories[c];
            for (var i = 0; i < cat.images.length; i++) {
                var img = cat.images[i];
                gridHtml += '<div class="obra-item" data-category="' + cat.filter_id + '" data-ref="' + img.ref + '" data-status="' + img.status + '">';
                gridHtml += '<div class="obra-img"><img src="' + img.path + '" alt="' + img.title + '" loading="lazy"></div>';
                gridHtml += '<div class="obra-info"><h3>' + img.title + '</h3><p>' + cat.display_name + '</p></div>';
                gridHtml += '</div>';
            }
        }
        obraGrid.innerHTML = gridHtml;

        // Re-bind filter buttons and obra items
        filterBtns = document.querySelectorAll('.filter-btn');
        obraItems = document.querySelectorAll('.obra-item');
        bindFilters();
        bindLightboxClicks();
    }

    function bindFilters() {
        for (var f = 0; f < filterBtns.length; f++) {
            filterBtns[f].addEventListener('click', function () {
                var filter = this.getAttribute('data-filter');
                for (var b = 0; b < filterBtns.length; b++) filterBtns[b].classList.remove('active');
                this.classList.add('active');

                for (var item = 0; item < obraItems.length; item++) {
                    if (filter === 'all' || obraItems[item].getAttribute('data-category') === filter) {
                        obraItems[item].classList.remove('hidden');
                        obraItems[item].style.opacity = '0';
                        obraItems[item].style.transform = 'translateY(20px)';
                        (function(el, delay) {
                            setTimeout(function() {
                                el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                                el.style.opacity = '1';
                                el.style.transform = 'translateY(0)';
                            }, delay);
                        })(obraItems[item], item * 80);
                    } else {
                        obraItems[item].classList.add('hidden');
                    }
                }
            });
        }
    }

    function bindLightboxClicks() {
        obraItems = document.querySelectorAll('.obra-item');
        for (var oi = 0; oi < obraItems.length; oi++) {
            (function(index) {
                obraItems[index].addEventListener('click', function () {
                    var vis = getVisibleItems();
                    var visIndex = vis.indexOf(this);
                    if (visIndex !== -1) openLightbox(visIndex);
                });
            })(oi);
        }
    }

    // Load gallery data
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'gallery-data.json', true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            try {
                var data = JSON.parse(xhr.responseText);
                buildGallery(data);
            } catch(e) {
                console.error('Error parsing gallery-data.json:', e);
            }
        } else {
            console.warn('gallery-data.json not found. Run: python3 build_gallery.py');
        }
    };
    xhr.onerror = function() {
        console.warn('Could not load gallery-data.json');
    };
    xhr.send();

    // ============================================================
    // Lightbox with ref, title, status, buy button
    // ============================================================
    var lightbox = document.getElementById('lightbox');
    var lightboxImg = document.getElementById('lightboxImg');
    var lightboxRef = document.getElementById('lightboxRef');
    var lightboxTitle = document.getElementById('lightboxTitle');
    var lightboxCaption = document.getElementById('lightboxCaption');
    var lightboxAction = document.getElementById('lightboxAction');
    var lightboxClose = document.querySelector('.lightbox-close');
    var lightboxPrev = document.querySelector('.lightbox-prev');
    var lightboxNext = document.querySelector('.lightbox-next');
    var currentLightboxIndex = 0;
    var visibleItems = [];

    // Status labels per language
    var statusLabels = {
        sale:       { es: 'Interés de compra', en: 'Purchase interest', de: 'Kaufinteresse', fr: "Intérêt d'achat", it: "Interesse all'acquisto", zh: '购买意向', ja: '購入希望', fa: 'علاقه به خرید' },
        sold:       { es: 'Obra vendida', en: 'Artwork sold', de: 'Werk verkauft', fr: 'Œuvre vendue', it: 'Opera venduta', zh: '作品已售', ja: '売却済み', fa: 'اثر فروخته شده' },
        notforsale: { es: 'No disponible para su venta', en: 'Not available for sale', de: 'Nicht zum Verkauf', fr: 'Non disponible à la vente', it: 'Non disponibile per la vendita', zh: '非卖品', ja: '非売品', fa: 'برای فروش موجود نیست' }
    };

    function getVisibleItems() {
        var items = [];
        for (var v = 0; v < obraItems.length; v++) {
            if (!obraItems[v].classList.contains('hidden')) items.push(obraItems[v]);
        }
        return items;
    }

    function openLightbox(index) {
        visibleItems = getVisibleItems();
        currentLightboxIndex = index;
        updateLightboxContent();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    function updateLightboxContent() {
        var item = visibleItems[currentLightboxIndex];
        if (!item) return;
        var imgEl = item.querySelector('.obra-img');
        var realImg = imgEl.querySelector('img');
        var title = item.querySelector('h3').textContent;
        var desc = item.querySelector('.obra-info p').textContent;
        var ref = item.getAttribute('data-ref') || '';
        var status = item.getAttribute('data-status') || 'notforsale';
        var lang = currentLang || 'es';

        // Use real image if available, otherwise fall back to CSS art class
        if (realImg) {
            lightboxImg.className = 'lightbox-img';
            lightboxImg.style.backgroundImage = 'url(' + realImg.src + ')';
            lightboxImg.style.backgroundSize = 'contain';
            lightboxImg.style.backgroundPosition = 'center';
            lightboxImg.style.backgroundRepeat = 'no-repeat';
        } else {
            lightboxImg.className = 'lightbox-img ' + imgEl.className.replace('obra-img ', '');
            lightboxImg.style.backgroundImage = '';
        }
        lightboxRef.textContent = ref;
        lightboxTitle.textContent = title;
        lightboxCaption.textContent = desc;

        // Build action button
        lightboxAction.innerHTML = '';
        if (status === 'sale') {
            var btn = document.createElement('button');
            btn.className = 'lightbox-buy-btn';
            btn.textContent = statusLabels.sale[lang] || statusLabels.sale.es;
            btn.addEventListener('click', function () {
                closeLightbox();
                navigateToBuy(ref, title);
            });
            lightboxAction.appendChild(btn);
        } else {
            var span = document.createElement('span');
            span.className = 'lightbox-status';
            span.textContent = (statusLabels[status] && statusLabels[status][lang]) || statusLabels[status].es;
            lightboxAction.appendChild(span);
        }
    }

    function navigateToBuy(ref, title) {
        // Scroll to contact
        var contactSection = document.querySelector('#contacto');
        if (contactSection) {
            window.scrollTo({
                top: contactSection.getBoundingClientRect().top + window.pageYOffset - nav.offsetHeight,
                behavior: 'smooth'
            });
        }
        // Fill form fields after scroll
        setTimeout(function () {
            var motivoEl = document.getElementById('motivo');
            var asuntoEl = document.getElementById('asunto');
            if (motivoEl) motivoEl.value = 'compra';
            if (asuntoEl) asuntoEl.value = 'Interés en la compra de ' + ref + ' ' + title;
            // Trigger change to update subject auto-fill logic
            if (motivoEl) motivoEl.dispatchEvent(new Event('change'));
        }, 600);
    }

    // Note: lightbox click bindings are now in bindLightboxClicks() above

    lightboxClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', function (e) { if (e.target === lightbox) closeLightbox(); });
    lightboxPrev.addEventListener('click', function (e) {
        e.stopPropagation();
        currentLightboxIndex = (currentLightboxIndex - 1 + visibleItems.length) % visibleItems.length;
        updateLightboxContent();
    });
    lightboxNext.addEventListener('click', function (e) {
        e.stopPropagation();
        currentLightboxIndex = (currentLightboxIndex + 1) % visibleItems.length;
        updateLightboxContent();
    });
    document.addEventListener('keydown', function (e) {
        if (!lightbox.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') { currentLightboxIndex = (currentLightboxIndex - 1 + visibleItems.length) % visibleItems.length; updateLightboxContent(); }
        if (e.key === 'ArrowRight') { currentLightboxIndex = (currentLightboxIndex + 1) % visibleItems.length; updateLightboxContent(); }
    });

    // ============================================================
    // Scroll Animations
    // ============================================================
    function initScrollAnimations() {
        if (!('IntersectionObserver' in window)) {
            var all = document.querySelectorAll('.timeline-item, .prensa-card');
            for (var fa = 0; fa < all.length; fa++) all[fa].classList.add('visible');
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            for (var e = 0; e < entries.length; e++) {
                if (entries[e].isIntersecting) entries[e].target.classList.add('visible');
            }
        }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

        var animated = document.querySelectorAll('.timeline-item, .prensa-card');
        for (var ae = 0; ae < animated.length; ae++) observer.observe(animated[ae]);
    }
    initScrollAnimations();

    // ============================================================
    // Contact Form with auto-subject
    // ============================================================
    var contactForm = document.getElementById('contactForm');
    var formSuccess = document.getElementById('formSuccess');
    var motivoEl = document.getElementById('motivo');
    var asuntoEl = document.getElementById('asunto');

    // Auto-fill subject based on motivo selection (only if not already filled by buy-interest)
    var subjectTemplates = {
        compra: 'Interés en la compra de obra artística',
        obra: 'Consulta sobre obra artística',
        exposicion: 'Propuesta de exposición',
        colaboracion: 'Propuesta de colaboración artística',
        prensa: 'Consulta de prensa y medios',
        galeria: 'Consulta sobre Galería O+O',
        otro: ''
    };

    motivoEl.addEventListener('change', function () {
        var motivo = this.value;
        // Only auto-fill if the current subject is empty or matches a template
        // (don't override a specific artwork buy-interest subject)
        var currentSubject = asuntoEl.value;
        var isTemplate = !currentSubject;
        for (var key in subjectTemplates) {
            if (subjectTemplates[key] && currentSubject === subjectTemplates[key]) {
                isTemplate = true;
                break;
            }
        }
        // Also check if it starts with "Interés en la compra de EH-" (specific artwork)
        var isSpecificBuy = currentSubject.indexOf('Interés en la compra de EH-') === 0;

        if (motivo === 'compra' && isSpecificBuy) {
            // Keep the specific artwork subject
            return;
        }

        if (isTemplate || (!isSpecificBuy && motivo)) {
            asuntoEl.value = subjectTemplates[motivo] || '';
        }
    });

    var CONTACT_EMAIL = 'enriqueta.hueso@gmail.com';

    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var formData = {
            nombre: document.getElementById('nombre').value,
            email: document.getElementById('email').value,
            motivo: document.getElementById('motivo').value,
            asunto: asuntoEl.value,
            mensaje: document.getElementById('mensaje').value
        };
        if (!formData.nombre || !formData.email || !formData.motivo || !formData.mensaje) return;
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) return;

        var subject = formData.asunto || 'Contacto web: ' + formData.motivo;
        var bodyText =
            'Nombre: ' + formData.nombre + '\n' +
            'Email: ' + formData.email + '\n' +
            'Motivo: ' + formData.motivo + '\n' +
            'Asunto: ' + formData.asunto + '\n\n' +
            'Mensaje:\n' + formData.mensaje;

        var subjectEnc = encodeURIComponent(subject);
        var bodyEnc = encodeURIComponent(bodyText);

        // Try mailto: first - if no email client is installed, the browser
        // will not navigate away. We detect this with a timeout.
        var mailtoUrl = 'mailto:' + CONTACT_EMAIL + '?subject=' + subjectEnc + '&body=' + bodyEnc;
        var mailtoWorked = false;

        // Listen for blur (means a mail client opened)
        function onBlur() { mailtoWorked = true; }
        window.addEventListener('blur', onBlur);

        // Open mailto
        var mailtoWindow = window.open(mailtoUrl, '_self');

        // After a short delay, check if mailto worked. If not, show webmail options.
        setTimeout(function () {
            window.removeEventListener('blur', onBlur);

            if (!mailtoWorked) {
                showWebmailFallback(subject, bodyText, formData);
            }
        }, 1500);

        formSuccess.classList.add('show');
        contactForm.reset();
        setTimeout(function () { formSuccess.classList.remove('show'); }, 8000);
    });

    function showWebmailFallback(subject, body, formData) {
        var subjectEnc = encodeURIComponent(subject);
        var bodyEnc = encodeURIComponent(body);

        // Build webmail URLs
        var gmailUrl = 'https://mail.google.com/mail/?view=cm&fs=1'
            + '&to=' + encodeURIComponent(CONTACT_EMAIL)
            + '&su=' + subjectEnc
            + '&body=' + bodyEnc;

        var outlookUrl = 'https://outlook.live.com/mail/0/deeplink/compose?to=' + encodeURIComponent(CONTACT_EMAIL)
            + '&subject=' + subjectEnc
            + '&body=' + bodyEnc;

        var yahooUrl = 'https://compose.mail.yahoo.com/?to=' + encodeURIComponent(CONTACT_EMAIL)
            + '&subject=' + subjectEnc
            + '&body=' + bodyEnc;

        // Create fallback panel
        var panel = document.createElement('div');
        panel.className = 'email-fallback-panel';
        panel.innerHTML =
            '<div class="email-fallback-inner">' +
            '<p class="email-fallback-title">Elige c&oacute;mo enviar el mensaje:</p>' +
            '<div class="email-fallback-buttons">' +
            '<a href="' + gmailUrl + '" target="_blank" class="email-fallback-btn email-fb-gmail">Gmail</a>' +
            '<a href="' + outlookUrl + '" target="_blank" class="email-fallback-btn email-fb-outlook">Outlook</a>' +
            '<a href="' + yahooUrl + '" target="_blank" class="email-fallback-btn email-fb-yahoo">Yahoo</a>' +
            '<a href="mailto:' + CONTACT_EMAIL + '?subject=' + subjectEnc + '&body=' + bodyEnc + '" class="email-fallback-btn email-fb-mailto">Email App</a>' +
            '</div>' +
            '<button class="email-fallback-close">&times;</button>' +
            '</div>';

        document.body.appendChild(panel);
        requestAnimationFrame(function () { panel.classList.add('active'); });

        panel.querySelector('.email-fallback-close').addEventListener('click', function () {
            panel.classList.remove('active');
            setTimeout(function () { panel.remove(); }, 300);
        });

        // Auto-close after clicking any link
        var links = panel.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            links[i].addEventListener('click', function () {
                setTimeout(function () {
                    panel.classList.remove('active');
                    setTimeout(function () { panel.remove(); }, 300);
                }, 500);
            });
        }
    }

    // ============================================================
    // Smooth scroll
    // ============================================================
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    for (var al = 0; al < anchorLinks.length; al++) {
        anchorLinks[al].addEventListener('click', function (e) {
            var targetId = this.getAttribute('href');
            if (targetId === '#') return;
            var target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                window.scrollTo({ top: target.getBoundingClientRect().top + window.pageYOffset - nav.offsetHeight, behavior: 'smooth' });
            }
        });
    }

    // ============================================================
    // Reduced motion
    // ============================================================
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        var allAnim = document.querySelectorAll('.timeline-item, .prensa-card');
        for (var rm = 0; rm < allAnim.length; rm++) allAnim[rm].classList.add('visible');
    }

})();
