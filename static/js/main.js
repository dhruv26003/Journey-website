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

        /* ---- hover / focus interactions ---- */
        var section = document.querySelector('.hero-section');
        if (section) {
            section.addEventListener('mouseenter', function () {
                // Keep video playing continuously when cursor hovers over it
                var v = getVideo(slides[current]);
                if (v && v.paused) {
                    v.play().catch(function () { });
                }
            });
            section.addEventListener('mouseleave', function () {
                var v = getVideo(slides[current]);
                if (v && v.paused) {
                    v.play().catch(function () { });
                }
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
       3. Anniversary Memory Counter (Dual Milestones)
       ------------------------------------------------------- */
    function initMemoryCounter() {
        // Milestone 1: Together Since February 22, 2024 (22/02/2024)
        var togetherTimestamp = new Date(2024, 1, 22, 0, 0, 0).getTime();
        
        // Milestone 2: Dating Since May 23, 2024 (23/05/2024)
        var datingTimestamp = new Date(2024, 4, 23, 0, 0, 0).getTime();

        function updateMilestone(startTime, prefix) {
            var daysEl = document.getElementById(prefix + '-days');
            var hoursEl = document.getElementById(prefix + '-hours');
            var minsEl = document.getElementById(prefix + '-minutes');
            var secsEl = document.getElementById(prefix + '-seconds');

            if (!daysEl || !hoursEl || !minsEl || !secsEl) return;

            var now = new Date().getTime();
            var difference = now - startTime;
            if (difference < 0) return;

            var days = Math.floor(difference / (1000 * 60 * 60 * 24));
            var hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((difference % (1000 * 60)) / 1000);

            daysEl.textContent = days < 10 ? '0' + days : days;
            hoursEl.textContent = hours < 10 ? '0' + hours : hours;
            minsEl.textContent = minutes < 10 ? '0' + minutes : minutes;
            secsEl.textContent = seconds < 10 ? '0' + seconds : seconds;
        }

        function updateAllMilestones() {
            updateMilestone(togetherTimestamp, 'together');
            updateMilestone(datingTimestamp, 'dating');
        }

        // Initialize and update every second
        updateAllMilestones();
        setInterval(updateAllMilestones, 1000);
    }

    /* -------------------------------------------------------
       4. Swipeable Compliments Card Deck
       ------------------------------------------------------- */
    function initSwipeableDeck() {
        var container = document.getElementById('deck-container');
        var btnNext = document.getElementById('btn-next-card');
        var btnPrev = document.getElementById('btn-prev-card');
        if (!container || !btnNext || !btnPrev || !window.gsap) return;

        var isAnimating = false;

        function getCards() {
            return Array.from(container.querySelectorAll('.swipe-card'));
        }

        function swipeNext() {
            if (isAnimating) return;
            var cards = getCards();
            if (cards.length <= 1) return;

            isAnimating = true;
            // The top card is the last child of the container in the HTML
            var topCard = cards[cards.length - 1];

            // Slide out to the right, rotate, and fade out
            gsap.to(topCard, {
                x: 350,
                y: -30,
                rotation: 25,
                opacity: 0,
                duration: 0.5,
                ease: 'power2.inOut',
                onComplete: function () {
                    // Prepend the top card to make it the bottom card of the stack
                    container.prepend(topCard);
                    
                    // Reset card layout parameters silently in background
                    gsap.set(topCard, { x: 0, y: 24, rotation: 0, opacity: 0 });

                    // Re-align depth of the card stack
                    var newCards = getCards();
                    newCards.forEach(function (card, index) {
                        var depth = newCards.length - 1 - index;
                        if (depth === 0) {
                            gsap.to(card, {
                                x: 0, y: 0, rotation: 0, opacity: 1,
                                duration: 0.4, ease: 'back.out(1.2)'
                            });
                        } else if (depth === 1) {
                            gsap.to(card, {
                                x: 0, y: 8, rotation: -1.5, opacity: 0.95,
                                duration: 0.4, ease: 'power2.out'
                            });
                        } else if (depth === 2) {
                            gsap.to(card, {
                                x: 0, y: 16, rotation: 1.5, opacity: 0.9,
                                duration: 0.4, ease: 'power2.out'
                            });
                        } else {
                            gsap.set(card, { x: 0, y: 24, rotation: 0, opacity: 0 });
                        }
                    });

                    isAnimating = false;
                }
            });
        }

        function swipePrev() {
            if (isAnimating) return;
            var cards = getCards();
            if (cards.length <= 1) return;

            isAnimating = true;
            // The bottom card is the first child in HTML
            var bottomCard = cards[0];

            // Set up its entering properties on the far left
            gsap.set(bottomCard, { x: -350, y: -30, rotation: -25, opacity: 0 });
            
            // Move it to the end of container to make it the top card
            container.appendChild(bottomCard);

            // Animate it sliding in onto the stack
            gsap.to(bottomCard, {
                x: 0, y: 0, rotation: 0, opacity: 1,
                duration: 0.5, ease: 'back.out(1.2)',
                onComplete: function () {
                    // Align remaining items
                    var newCards = getCards();
                    newCards.forEach(function (card, index) {
                        var depth = newCards.length - 1 - index;
                        if (depth === 1) {
                            gsap.to(card, { x: 0, y: 8, rotation: -1.5, opacity: 0.95, duration: 0.3 });
                        } else if (depth === 2) {
                            gsap.to(card, { x: 0, y: 16, rotation: 1.5, opacity: 0.9, duration: 0.3 });
                        } else if (depth >= 3) {
                            gsap.set(card, { x: 0, y: 24, rotation: 0, opacity: 0 });
                        }
                    });
                    isAnimating = false;
                }
            });
        }

        // Click Event Bindings
        btnNext.addEventListener('click', swipeNext);
        btnPrev.addEventListener('click', swipePrev);

        // Touch Swipe Event Bindings
        var startX = 0;
        container.addEventListener('touchstart', function (e) {
            startX = e.touches[0].clientX;
        }, { passive: true });

        container.addEventListener('touchend', function (e) {
            var diffX = e.changedTouches[0].clientX - startX;
            if (Math.abs(diffX) > 60) {
                if (diffX > 0) {
                    swipePrev();
                } else {
                    swipeNext();
                }
            }
        }, { passive: true });
    }

    /* -------------------------------------------------------
       Bootstrap
       ------------------------------------------------------- */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initTypewriter();
            initSlideshow();
            initMemoryCounter();
            initSwipeableDeck();
        });
    } else {
        initTypewriter();
        initSlideshow();
        initMemoryCounter();
        initSwipeableDeck();
    }

})();
