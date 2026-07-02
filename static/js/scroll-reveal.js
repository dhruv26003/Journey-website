/**
 * scroll-reveal.js
 * High-performance scroll-triggered reveal animations using IntersectionObserver.
 * Also supports auto-staggering child elements inside a .scroll-stagger container.
 */
(function () {
    'use strict';

    // 1. Accessibility guard: if reduced motion is enabled, do nothing (CSS handles showing everything)
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    function initScrollReveal() {
        // 2. Setup Stagger delays for container elements
        var staggers = document.querySelectorAll('.scroll-stagger');
        staggers.forEach(function (container) {
            // Find direct or indirect child scroll-reveal elements
            var reveals = container.querySelectorAll('.scroll-reveal');
            reveals.forEach(function (el, index) {
                // Calculate delay in milliseconds, cycling every 4 elements to keep it tight in grid rows
                var delay = (index % 4) * 100; 
                el.style.setProperty('--scroll-delay', delay + 'ms');
            });
        });



        // 3. Set up IntersectionObserver
        var observerOptions = {
            root: null, // viewport
            rootMargin: '0px 0px -10% 0px', // trigger slightly before elements enter view
            threshold: 0.05 // trigger when 5% is visible
        };

        var observer = new IntersectionObserver(function (entries, observerInstance) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    // Stop observing once animated in
                    observerInstance.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // 4. Observe all elements with .scroll-reveal class
        var revealElements = document.querySelectorAll('.scroll-reveal');
        revealElements.forEach(function (el) {
            observer.observe(el);
        });
    }

    // Bootstrap
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initScrollReveal);
    } else {
        initScrollReveal();
    }
})();
