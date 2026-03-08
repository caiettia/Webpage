(function () {
    'use strict';

    var navToggle = document.getElementById('nav-toggle');
    var navMenu = document.getElementById('nav-menu');
    var navBackdrop = document.getElementById('nav-backdrop');
    var iconOpen = document.querySelector('.js-nav-icon-open');
    var iconClose = document.querySelector('.js-nav-icon-close');

    function isMenuOpen() {
        return navMenu && navMenu.classList.contains('is-open');
    }

    function setMenuOpen(open) {
        if (!navMenu || !navToggle) return;
        if (open) {
            navMenu.classList.add('is-open');
            navToggle.setAttribute('aria-expanded', 'true');
            if (iconOpen) iconOpen.classList.add('hidden');
            if (iconClose) iconClose.classList.remove('hidden');
            if (navBackdrop) {
                navBackdrop.classList.remove('opacity-0', 'pointer-events-none');
            }
            document.documentElement.style.overflow = 'hidden';
        } else {
            navMenu.classList.remove('is-open');
            navToggle.setAttribute('aria-expanded', 'false');
            if (iconOpen) iconOpen.classList.remove('hidden');
            if (iconClose) iconClose.classList.add('hidden');
            if (navBackdrop) {
                navBackdrop.classList.add('opacity-0', 'pointer-events-none');
            }
            document.documentElement.style.overflow = '';
        }
    }

    function toggleMenu() {
        setMenuOpen(!isMenuOpen());
    }

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', toggleMenu);
        if (navBackdrop) {
            navBackdrop.addEventListener('click', function () { setMenuOpen(false); });
        }

        // Close menu when clicking a nav link (mobile)
        navMenu.addEventListener('click', function (e) {
            var link = e.target.closest('a');
            if (link && (link.getAttribute('href') || '').startsWith('/')) {
                setMenuOpen(false);
            }
        });

        // Close on escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && isMenuOpen()) setMenuOpen(false);
        });

        // Close when resizing to desktop
        window.addEventListener('resize', function () {
            if (window.matchMedia('(min-width: 768px)').matches) {
                setMenuOpen(false);
            }
        });
    }
})();
