document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    // navToggle.addEventListener('click', function() {
    //     navMenu.classList.toggle('show');
    // });

    navToggle.addEventListener('click', function() {
        if ( navMenu.classList.contains('nav-menu')) {
            navMenu.classList.remove('nav-menu');
            navMenu.classList.add('nav-menu-show');
        } else {
            navMenu.classList.remove('nav-menu-show');
            navMenu.classList.add('nav-menu');
        }
    });
});