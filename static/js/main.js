/**
 * main.js — Home page interactions
 *
 * 1. Typewriter effect on the hero heading
 * 2. Hero slideshow auto-advance (photos + videos)
 *    - Videos auto-pause when slide is hidden, play when active
 *    - Video slides advance after the video ends (or after 12s max)
 * 3. Dot button manual navigation
 */

(function () {
    'use strict';

    /* -------------------------------------------------------
       1. Typewriter effect
       ------------------------------------------------------- */
    function initTypewriter() {
        var el = document.getElementById('hero-heading');
        if (!el) return;

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            el.textContent = el.dataset.text || '';
            return;
        }

        var text = el.dataset.text || '';
        var index = 0;
        el.textContent = '';

        var CHAR_DELAY_MS = 60;
        var START_DELAY_MS = 400;

        function typeNextChar() {
            if (index < text.length) {
                el.textContent += text.charAt(index);
                index++;
                setTimeout(typeNextChar, CHAR_DELAY_MS);
            }
        }

        setTimeout(typeNextChar, START_DELAY_MS);
    }

    /* -------------------------------------------------------
       2. Hero slideshow
       ------------------------------------------------------- */
    function initSlideshow() {
        var slides = Array.from(document.querySelectorAll('.hero-slide'));
        var dots = Array.from(document.querySelectorAll('.slideshow-dot'));
        if (slides.length <= 1) return;

        var current = 0;
        var PHOTO_MS = 5000;   // 5 s for photos
        var VIDEO_MAX_MS = 15000;  // safety cap for very long videos
        var timer = null;
        var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        /* ---- helpers ---- */
        function getVideo(slideEl) {
            return slideEl.querySelector('video');
        }

        function isVideoSlide(slideEl) {
            return slideEl.dataset.isVideo === 'true';
        }

        function pauseSlide(slideEl) {
            var v = getVideo(slideEl);
            if (v) { v.pause(); }
        }

        function playSlide(slideEl) {
            var v = getVideo(slideEl);
            if (v) {
                v.currentTime = 0;
                v.play().catch(function () { /* autoplay blocked — ok */ });
            }
        }

        /* ---- navigate to a slide ---- */
        function goTo(index) {
            index = ((index % slides.length) + slides.length) % slides.length;
            if (index === current) return;

            // Deactivate current
            pauseSlide(slides[current]);
            slides[current].classList.remove('active');
            if (dots.length) {
                dots[current].classList.remove('active');
                dots[current].setAttribute('aria-selected', 'false');
            }

            current = index;

            // Activate new
            slides[current].classList.add('active');
            if (dots.length) {
                dots[current].classList.add('active');
                dots[current].setAttribute('aria-selected', 'true');
            }
            playSlide(slides[current]);
            scheduleNext();
        }

        /* ---- timer management ---- */
        function clearTimer() {
            if (timer) {
                clearTimeout(timer);
                clearInterval(timer);
                timer = null;
            }
        }

        function scheduleNext() {
            clearTimer();
            if (reducedMotion) return;

            var slide = slides[current];

            if (isVideoSlide(slide)) {
                // Advance when video ends, but cap at VIDEO_MAX_MS
                var vid = getVideo(slide);
                if (vid) {
                    var onEnded = function () {
                        vid.removeEventListener('ended', onEnded);
                        clearTimer();
                        goTo(current + 1);
                    };
                    vid.addEventListener('ended', onEnded);
                    // Safety cap
                    timer = setTimeout(function () {
                        vid.removeEventListener('ended', onEnded);
                        goTo(current + 1);
                    }, VIDEO_MAX_MS);
                } else {
                    timer = setTimeout(function () { goTo(current + 1); }, PHOTO_MS);
                }
            } else {
                timer = setTimeout(function () { goTo(current + 1); }, PHOTO_MS);
            }
        }

        /* ---- dot interactions ---- */
        dots.forEach(function (dot) {
            dot.addEventListener('click', function () {
                var target = parseInt(dot.dataset.dot, 10);
                if (!isNaN(target) && target !== current) {
                    goTo(target);
                }
            });
            dot.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    dot.click();
                }
            });
        });

        /* ---- pause on hover / focus ---- */
        var section = document.querySelector('.hero-section');
        if (section) {
            section.addEventListener('mouseenter', function () {
                clearTimer();
                var v = getVideo(slides[current]);
                if (v) v.pause();
            });
            section.addEventListener('mouseleave', function () {
                var v = getVideo(slides[current]);
                if (v) v.play().catch(function () { });
                scheduleNext();
            });
            section.addEventListener('focusin', function () {
                clearTimer();
            });
            section.addEventListener('focusout', function () {
                scheduleNext();
            });
        }

        /* ---- kick off ---- */
        // Play first slide if it's a video
        playSlide(slides[0]);
        if (!reducedMotion) scheduleNext();
    }

    /* -------------------------------------------------------
       Bootstrap
       ------------------------------------------------------- */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initTypewriter();
            initSlideshow();
        });
    } else {
        initTypewriter();
        initSlideshow();
    }

})();
