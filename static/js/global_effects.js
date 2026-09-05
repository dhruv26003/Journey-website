/**
 * global_effects.js
 * Premium interactive background particles, custom cursor, clicking reactions, and music visualizer.
 */

(function () {
    'use strict';

    // Guard for reduced motion preferences (Accessibility)
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* -------------------------------------------------------------
       1. Custom Romantic Heart Cursor & Sparkle Trail
       ------------------------------------------------------------- */
    function initCustomCursor() {
        if (prefersReducedMotion || window.innerWidth < 768) return;

        const cursorHeart = document.getElementById('custom-cursor-heart');
        const cursorAura = document.getElementById('custom-cursor-aura');
        if (!cursorHeart || !cursorAura) return;

        let mouseX = -100, mouseY = -100;
        let ringX = -100, ringY = -100;
        let lastTrailX = -100, lastTrailY = -100;
        let isVisible = false;

        const trailSymbols = ['♥', '✨', '🌸', '💕', '✦'];
        const trailColors = ['#ff758c', '#ff4b6e', '#ffa0b4', '#fbc2eb', '#e84393'];

        // Spawn a cute micro heart / sparkle trail particle
        function spawnTrail(x, y) {
            if (prefersReducedMotion) return;
            const particle = document.createElement('span');
            particle.className = 'cursor-trail-particle';
            particle.setAttribute('aria-hidden', 'true');
            particle.textContent = trailSymbols[Math.floor(Math.random() * trailSymbols.length)];

            // Randomize trajectory and style
            const tx = (Math.random() - 0.5) * 40;
            const ty = -15 - Math.random() * 30; // Float upwards
            const rot = (Math.random() - 0.5) * 60;
            const size = Math.floor(Math.random() * 6 + 10); // 10px to 16px
            const color = trailColors[Math.floor(Math.random() * trailColors.length)];

            particle.style.setProperty('--start-x', `${x}px`);
            particle.style.setProperty('--start-y', `${y}px`);
            particle.style.setProperty('--end-x', `${x + tx}px`);
            particle.style.setProperty('--end-y', `${y + ty}px`);
            particle.style.setProperty('--rot', `${rot}deg`);
            particle.style.fontSize = `${size}px`;
            particle.style.color = color;

            document.body.appendChild(particle);

            particle.addEventListener('animationend', () => {
                particle.remove();
            }, { once: true });

            // Fallback cleanup
            setTimeout(() => {
                if (particle.parentNode) particle.remove();
            }, 800);
        }

        function updatePosition(e) {
            mouseX = e.clientX;
            mouseY = e.clientY;

            if (!isVisible) {
                isVisible = true;
                cursorHeart.style.opacity = '1';
                cursorAura.style.opacity = '1';
                ringX = mouseX;
                ringY = mouseY;
            }

            // Direct instant tracking for heart pointer
            cursorHeart.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0) rotate(-12deg)`;

            // Spawn trail particle if mouse has moved sufficiently (approx 22px)
            const dist = Math.hypot(mouseX - lastTrailX, mouseY - lastTrailY);
            if (dist > 22) {
                spawnTrail(mouseX, mouseY);
                lastTrailX = mouseX;
                lastTrailY = mouseY;
            }
        }

        window.addEventListener('mousemove', updatePosition, { passive: true });
        document.addEventListener('mousemove', updatePosition, { passive: true });

        // Hide when mouse leaves window
        document.addEventListener('mouseleave', () => {
            isVisible = false;
            cursorHeart.style.opacity = '0';
            cursorAura.style.opacity = '0';
        });

        document.addEventListener('mouseenter', (e) => {
            isVisible = true;
            if (e.clientX !== undefined && e.clientY !== undefined) {
                mouseX = e.clientX;
                mouseY = e.clientY;
                ringX = mouseX;
                ringY = mouseY;
                cursorHeart.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0) rotate(-12deg)`;
            }
            cursorHeart.style.opacity = '1';
            cursorAura.style.opacity = '1';
        });

        // Smooth trailing aura ring (lerp animation)
        function animateAura() {
            if (isVisible) {
                ringX += (mouseX - ringX) * 0.22;
                ringY += (mouseY - ringY) * 0.22;
                cursorAura.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`;
            }
            requestAnimationFrame(animateAura);
        }
        animateAura();

        // Hover effects on interactive elements
        const hoverTargets = 'a, button, [role="button"], .memory-card, .bv-card, .btn-hero-primary, .btn-hero-outline, .year-btn, .nav-link, .envelope';

        document.addEventListener('mouseover', (e) => {
            if (e.target.closest(hoverTargets)) {
                cursorAura.classList.add('cursor-hover');
                cursorHeart.classList.add('cursor-hover');
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (e.target.closest(hoverTargets)) {
                cursorAura.classList.remove('cursor-hover');
                cursorHeart.classList.remove('cursor-hover');
            }
        });

        // Click animations
        document.addEventListener('mousedown', () => {
            cursorHeart.classList.add('cursor-click');
            cursorAura.classList.add('cursor-click');

            // Extra mini burst of 2-3 sparkle particles on click
            for (let i = 0; i < 3; i++) {
                spawnTrail(mouseX, mouseY);
            }
        });

        document.addEventListener('mouseup', () => {
            cursorHeart.classList.remove('cursor-click');
            cursorAura.classList.remove('cursor-click');
        });
    }

    /* -------------------------------------------------------------
       2. Falling Particles (Sakura & Hearts Canvas)
       ------------------------------------------------------------- */
    function initCanvasParticles() {
        if (prefersReducedMotion) return;

        const canvas = document.getElementById('particles-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let particles = [];
        const maxParticles = 40;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        class Particle {
            constructor() {
                this.reset();
            }

            reset() {
                this.x = Math.random() * canvas.width;
                this.y = -20 - Math.random() * 50;
                this.size = Math.random() * 6 + 4;
                this.speedY = Math.random() * 1.2 + 0.8;
                this.speedX = Math.random() * 0.8 - 0.4;
                this.type = Math.random() > 0.45 ? 'petal' : 'heart'; // Petal or Heart
                this.opacity = Math.random() * 0.4 + 0.3;
                this.rotation = Math.random() * Math.PI * 2;
                this.rotationSpeed = (Math.random() - 0.5) * 0.02;
                this.swayAmplitude = Math.random() * 1.5 + 0.5;
                this.swaySpeed = Math.random() * 0.02 + 0.01;
                this.time = Math.random() * 100;
            }

            update() {
                this.time += this.swaySpeed;
                this.y += this.speedY;
                this.x += this.speedX + Math.sin(this.time) * this.swayAmplitude;
                this.rotation += this.rotationSpeed;

                if (this.y > canvas.height + 20) {
                    this.reset();
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                ctx.globalAlpha = this.opacity;

                if (this.type === 'petal') {
                    // Draw Sakura petal shape
                    ctx.fillStyle = '#ffb7c5'; // Soft pink Sakura color
                    ctx.beginPath();
                    ctx.ellipse(0, 0, this.size, this.size * 1.6, 0, 0, Math.PI * 2);
                    ctx.fill();
                    // Draw inner shading line
                    ctx.strokeStyle = '#ffa0b4';
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(0, -this.size * 1.6);
                    ctx.lineTo(0, this.size * 1.6);
                    ctx.stroke();
                } else {
                    // Draw cute Heart shape
                    ctx.fillStyle = '#e8a598'; // Muted warm peach/pink
                    ctx.beginPath();
                    ctx.moveTo(0, 0);
                    // Draw left heart curve
                    ctx.bezierCurveTo(-this.size, -this.size, -this.size * 1.8, this.size * 0.2, 0, this.size * 1.5);
                    // Draw right heart curve
                    ctx.bezierCurveTo(this.size * 1.8, this.size * 0.2, this.size, -this.size, 0, 0);
                    ctx.closePath();
                    ctx.fill();
                }
                ctx.restore();
            }
        }

        // Initialize particle array
        for (let i = 0; i < maxParticles; i++) {
            particles.push(new Particle());
            // Pre-distribute particles vertically on load so they don't all fall from top together
            particles[i].y = Math.random() * canvas.height;
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            requestAnimationFrame(animate);
        }
        animate();
    }

    /* -------------------------------------------------------------
       3. Floating Heart Reaction on Click
       ------------------------------------------------------------- */
    function initClickReaction() {
        if (prefersReducedMotion) return;

        const reactionSymbols = ['❤️', '💖', '✨', '🌸', '💕'];
        const colors = ['#c0605a', '#e8a598', '#f2c4a0', '#9b59b6', '#ffb7c5'];

        document.addEventListener('click', (e) => {
            // Ignore clicking on links, buttons, or scrollbars to prevent visual clutter
            if (e.target.closest('a, button, input, select, textarea')) return;

            const particleCount = gsap.utils.random(4, 7, 1);

            for (let i = 0; i < particleCount; i++) {
                const element = document.createElement('span');
                element.className = 'click-reaction-heart';
                element.setAttribute('aria-hidden', 'true');
                element.textContent = reactionSymbols[Math.floor(Math.random() * reactionSymbols.length)];
                
                // Style element
                element.style.position = 'fixed';
                element.style.left = e.clientX + 'px';
                element.style.top = e.clientY + 'px';
                element.style.fontSize = gsap.utils.random(1.0, 1.8) + 'rem';
                element.style.color = colors[Math.floor(Math.random() * colors.length)];
                element.style.pointerEvents = 'none';
                element.style.zIndex = '9999';
                
                document.body.appendChild(element);

                // GSAP animate upward floating and fading
                gsap.fromTo(element, 
                    {
                        x: 0,
                        y: 0,
                        scale: 0.2,
                        opacity: 1,
                        rotation: 0
                    },
                    {
                        x: gsap.utils.random(-80, 80),
                        y: gsap.utils.random(-150, -250),
                        scale: gsap.utils.random(1.2, 1.8),
                        opacity: 0,
                        rotation: gsap.utils.random(-180, 180),
                        duration: gsap.utils.random(1.2, 2.0),
                        ease: "power2.out",
                        onComplete: () => {
                            element.remove();
                        }
                    }
                );
            }
        });
    }

    /* -------------------------------------------------------------
       4. Music Visualizer Animation
       ------------------------------------------------------------- */
    function initMusicVisualizer() {
        const visualizer = document.querySelector('.audio-visualizer');
        const audio = document.getElementById('siteAudio') || document.getElementById('bg-audio');
        
        if (!visualizer || !audio) return;

        // Populate bars if they don't exist
        if (visualizer.children.length === 0) {
            for (let i = 0; i < 4; i++) {
                const bar = document.createElement('span');
                bar.className = 'visualizer-bar';
                visualizer.appendChild(bar);
            }
        }

        const bars = visualizer.querySelectorAll('.visualizer-bar');
        let isPlaying = false;
        let animationFrameId = null;

        function updateVisualizerAnimation() {
            if (!isPlaying) {
                // Shrink bars back to flat
                bars.forEach(bar => {
                    bar.style.transform = 'scaleY(0.2)';
                });
                return;
            }

            // Animate each bar with random heights
            bars.forEach((bar, index) => {
                const scale = Math.random() * 0.8 + 0.25; // Scale range [0.25, 1.05]
                bar.style.transform = `scaleY(${scale})`;
            });

            // Delay next state slightly to look like sound frequencies rather than vibrating noise
            setTimeout(() => {
                if (isPlaying) {
                    animationFrameId = requestAnimationFrame(updateVisualizerAnimation);
                }
            }, 80);
        }

        // Monitor playing state by checking audio event triggers
        audio.addEventListener('play', () => {
            isPlaying = true;
            visualizer.classList.add('playing');
            updateVisualizerAnimation();
        });

        audio.addEventListener('pause', () => {
            isPlaying = false;
            visualizer.classList.remove('playing');
            cancelAnimationFrame(animationFrameId);
            updateVisualizerAnimation();
        });

        audio.addEventListener('ended', () => {
            isPlaying = false;
            visualizer.classList.remove('playing');
            cancelAnimationFrame(animationFrameId);
            updateVisualizerAnimation();
        });

        // Initialize state based on audio status on page load
        if (!audio.paused) {
            isPlaying = true;
            visualizer.classList.add('playing');
            updateVisualizerAnimation();
        }
    }

    /* -------------------------------------------------------------
       Bootstrap & Load
       ------------------------------------------------------------- */
    document.addEventListener('DOMContentLoaded', () => {
        initCustomCursor();
        initCanvasParticles();
        initClickReaction();
        initMusicVisualizer();
    });

})();
