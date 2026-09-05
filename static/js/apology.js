/**
 * apology.js — Interactive 3D Envelope Opening & Lined-Paper Letter Reveal
 */

(function () {
    'use strict';

    // 1. Accessibility guard
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* -------------------------------------------------------
       Typewriter Letter Text Reveal (via GSAP & SplitType)
       ------------------------------------------------------- */
    let revealTimeline = null;

    function buildLetterReveal() {
        const apologyBody = document.querySelector('.apology-body');
        const heading = document.querySelector('.letter-title');
        
        if (!apologyBody || !window.gsap || !window.SplitType) return null;

        const tl = gsap.timeline({ paused: true });

        // 1. Fade in heading first
        if (heading) {
            const headingSplit = new SplitType(heading, { types: 'chars' });
            tl.from(headingSplit.chars, {
                opacity: 0,
                y: 15,
                stagger: 0.04,
                duration: 0.7,
                ease: "back.out(1.5)",
                onComplete: () => headingSplit.revert()
            });
        }

        // 2. Select paragraphs/lines in letter body and reveal them word-by-word
        let elementsToSplit = Array.from(apologyBody.querySelectorAll('p, blockquote, em, li'));
        if (elementsToSplit.length === 0) {
            // If the body has raw text and no standard block elements, split the body itself!
            elementsToSplit = [apologyBody];
        }

        elementsToSplit.forEach((element) => {
            const split = new SplitType(element, { types: 'words' });
            tl.from(split.words, {
                opacity: 0,
                y: 8,
                stagger: 0.03,
                duration: 0.55,
                ease: "power2.out"
            }, "-=0.15"); // overlap slightly with previous element
        });

        return tl;
    }

    /* -------------------------------------------------------
       3D Envelope Interactions
       ------------------------------------------------------- */
    function initEnvelope() {
        const envelope = document.getElementById('envelope');
        const letter = document.getElementById('envelope-letter');
        if (!envelope || !letter) return;

        // Build the text reveal timeline ahead of time
        revealTimeline = buildLetterReveal();

        let isOpen = false;

        function openLetter() {
            if (isOpen) return;
            isOpen = true;

            envelope.classList.add('open');
            envelope.setAttribute('aria-label', 'The letter is open');

            // Sequential timing adjustments matching CSS transition durations
            
            // 1. Wait for flap flip to end (0.6s) before shifting flap z-index
            setTimeout(() => {
                const flap = envelope.querySelector('.envelope-flap');
                if (flap) {
                    flap.style.zIndex = '1'; // Push flap behind pocket
                }
            }, 550);

            // 2. Wait for envelope slide-up to fully open (0.8s) before starting text reveal
            setTimeout(() => {
                letter.focus();
                if (revealTimeline) {
                    revealTimeline.play();
                }
            }, 750);
        }

        // Handle mouse click
        envelope.addEventListener('click', (e) => {
            // Prevent triggering if clicked inside the letter itself (e.g. scrolling text)
            if (e.target.closest('#envelope-letter')) return;
            openLetter();
        });

        // Handle keyboard navigation (Space / Enter)
        envelope.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openLetter();
            }
        });
    }

    /* -------------------------------------------------------
       Bootstrap
       ------------------------------------------------------- */
    document.addEventListener('DOMContentLoaded', () => {
        initEnvelope();
        
        // If reduced motion is preferred, immediately trigger typing reveal
        if (prefersReducedMotion && revealTimeline) {
            const envelope = document.getElementById('envelope');
            if (envelope) {
                envelope.classList.add('open');
            }
            revealTimeline.play();
        }
    });

})();
