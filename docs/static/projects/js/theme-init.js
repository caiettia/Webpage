// Run before styles paint; also keeps mobile navigation usable without JavaScript.
(function () {
    document.documentElement.classList.add('js');
    var stored;
    try { stored = localStorage.getItem('theme-preference'); } catch (error) {}
    var dark = stored === 'dark' || (stored !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.classList.toggle('dark', dark);
})();
