(function () {
    'use strict';
    var root = document.documentElement;
    var themeButton = document.getElementById('theme-toggle');
    var media = matchMedia('(prefers-color-scheme: dark)');
    function storedTheme() {
        try { return localStorage.getItem('theme-preference'); } catch (error) { return null; }
    }
    function applyTheme(dark, persist) {
        root.classList.toggle('dark', dark);
        themeButton.setAttribute('aria-pressed', String(dark));
        themeButton.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
        themeButton.title = themeButton.getAttribute('aria-label');
        themeButton.querySelector('.js-theme-icon-moon').classList.toggle('hidden', dark);
        themeButton.querySelector('.js-theme-icon-sun').classList.toggle('hidden', !dark);
        if (persist) {
            try { localStorage.setItem('theme-preference', dark ? 'dark' : 'light'); } catch (error) {}
        }
    }
    themeButton.hidden = false;
    applyTheme(root.classList.contains('dark'), false);
    themeButton.addEventListener('click', function () { applyTheme(!root.classList.contains('dark'), true); });
    media.addEventListener('change', function () {
        if (!['dark', 'light'].includes(storedTheme())) applyTheme(media.matches, false);
    });

    var toggle = document.getElementById('nav-toggle');
    var menu = document.getElementById('nav-menu');
    var backdrop = document.getElementById('nav-backdrop');
    var desktop = matchMedia('(min-width: 768px)');
    toggle.hidden = false;
    function setMenuOpen(open, restoreFocus) {
        open = open && !desktop.matches;
        menu.classList.toggle('is-open', open);
        menu.inert = !desktop.matches && !open;
        toggle.setAttribute('aria-expanded', String(open));
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        toggle.querySelector('.js-nav-icon-open').classList.toggle('hidden', open);
        toggle.querySelector('.js-nav-icon-close').classList.toggle('hidden', !open);
        backdrop.classList.toggle('opacity-0', !open);
        backdrop.classList.toggle('pointer-events-none', !open);
        root.style.overflow = open ? 'hidden' : '';
        if (restoreFocus) toggle.focus();
    }
    setMenuOpen(false);
    toggle.addEventListener('click', function () {
        var open = toggle.getAttribute('aria-expanded') !== 'true';
        setMenuOpen(open);
        if (open) menu.querySelector('a').focus();
    });
    backdrop.addEventListener('click', function () { setMenuOpen(false, true); });
    menu.addEventListener('click', function (event) {
        if (event.target.closest('a')) setMenuOpen(false);
    });
    document.addEventListener('keydown', function (event) {
        if (toggle.getAttribute('aria-expanded') !== 'true') return;
        if (event.key === 'Escape') { setMenuOpen(false, true); return; }
        if (event.key !== 'Tab') return;
        // Keep focus inside the visible menu and its controls while the backdrop is open.
        var controls = Array.from(menu.querySelectorAll('a')).concat([themeButton, toggle]);
        var first = controls[0], last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    desktop.addEventListener('change', function () {
        var focusWillBeHidden = !desktop.matches && menu.contains(document.activeElement);
        setMenuOpen(false, focusWillBeHidden);
    });
})();
