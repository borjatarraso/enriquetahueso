/* Galería O+O - Site JavaScript */

// Mobile menu toggle
document.querySelector('.menu-toggle').addEventListener('click', function() {
    document.querySelector('.nav-links').classList.toggle('open');
});

// Image lightbox for content images
(function() {
    // Create overlay element
    var overlay = document.createElement('div');
    overlay.className = 'img-overlay';
    overlay.innerHTML = '<button class="img-overlay-close">&times;</button><img src="" alt="">';
    document.body.appendChild(overlay);

    var overlayImg = overlay.querySelector('img');
    var closeBtn = overlay.querySelector('.img-overlay-close');

    function openOverlay(src) {
        overlayImg.src = src;
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeOverlay() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    overlay.addEventListener('click', closeOverlay);
    closeBtn.addEventListener('click', function(e) { e.stopPropagation(); closeOverlay(); });
    overlayImg.addEventListener('click', function(e) { e.stopPropagation(); });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeOverlay();
    });

    // Intercept clicks on image links within page-content
    var content = document.querySelector('.page-content');
    if (content) {
        content.addEventListener('click', function(e) {
            var link = e.target.closest('a');
            if (!link) return;
            var href = link.getAttribute('href') || '';
            if (href.match(/\.(jpg|jpeg|png|gif)$/i)) {
                e.preventDefault();
                openOverlay(href);
            }
        });
    }

    // Also handle broken images - hide them
    var imgs = document.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) {
        imgs[i].addEventListener('error', function() {
            this.style.display = 'none';
        });
    }
})();
