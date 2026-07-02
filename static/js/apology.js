/**
 * apology.js — Floating petal / heart background & letter typing reveal for the Apology page
 */

(function () {
    'use strict';

    // 1. Accessibility guard
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    /* -------------------------------------------------------
       GSAP Floating Hearts / Petals
       ------------------------------------------------------- */
    const SYMBOLS = ['\u2764', '\u273F', '\u2665', '\u2728']; // ❤ ✿ ♥ ✨
    const SPAWN_INTERVAL_MS = 600;

    function spawnHeart() {
        const symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
        const el = document.createElement('span');
        el.className = 'petal';
        el.setAttribute('aria-hidden', 'true');
        el.textContent = symbol;
        
        // Style variables
        const size = gsap.utils.random(1.2, 2.4);
        el.style.fontSize = size + 'rem';
        
        // Random warm tones
        const colors = ['#c0605a', '#e8a598', '#f2c4a0', '#9b59b6'];
        el.style.color = colors[Math.floor(Math.random() * colors.length)];
        
        el.style.left = gsap.utils.random(0, 95) + 'vw';
        el.style.top = '-50px';
        
        document.body.appendChild(el);

        // GSAP falling motion with sway and spin
        gsap.fromTo(el, 
            { y: 0, opacity: 0, rotation: 0 },
            { 
                y: window.innerHeight + 100, 
                opacity: gsap.utils.random(0.35, 0.85), 
                rotation: gsap.utils.random(180, 720),
                x: "+=" + gsap.utils.random(-80, 80),
                duration: gsap.utils.random(6, 12),
                ease: "none",
                onComplete: () => {
                    el.remove();
                }
            }
        );
        
        // Fade in initially
        gsap.to(el, { opacity: gsap.utils.random(0.4, 0.9), duration: 1.5 });
    }

    function initFloatingPetals() {
        if (!window.gsap) return;
        
        // Spawn at a steady rate
        setInterval(spawnHeart, SPAWN_INTERVAL_MS);
    }

    /* -------------------------------------------------------
       SplitType Letter Reveal
       ------------------------------------------------------- */
    function initLetterReveal() {
        const apologyBody = document.querySelector('.apology-body');
        const heading = document.querySelector('.apology-card h1');
        
        if (!apologyBody || !window.gsap || !window.SplitType) return;

        const tl = gsap.timeline();

        // 1. Reveal heading first
        if (heading) {
            const headingSplit = new SplitType(heading, { types: 'chars' });
            tl.from(headingSplit.chars, {
                opacity: 0,
                y: 20,
                stagger: 0.04,
                duration: 0.8,
                ease: "back.out(1.5)",
                onComplete: () => headingSplit.revert()
            });
        }

        // 2. Select all paragraphs/lines in letter body and reveal them word-by-word
        const elementsToSplit = apologyBody.querySelectorAll('p, blockquote, em');
        if (elementsToSplit.length > 0) {
            elementsToSplit.forEach((element) => {
                const split = new SplitType(element, { types: 'words' });
                tl.from(split.words, {
                    opacity: 0,
                    y: 10,
                    stagger: 0.04,
                    duration: 0.65,
                    ease: "power2.out"
                }, "-=0.2"); // overlap slightly with previous element
            });
        }
    }

    /* -------------------------------------------------------
       Bootstrap
       ------------------------------------------------------- */
    document.addEventListener('DOMContentLoaded', () => {
        initFloatingPetals();
        initLetterReveal();
    });

})();
