/**
 * animations.js
 * Premium frontend animations using GSAP, ScrollTrigger, SplitType, and Three.js
 */

(function () {
    'use strict';

    // 1. Accessibility guard: skip animations if reduced motion is preferred
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    /* -------------------------------------------------------------
       3D Hearts Background (Three.js)
       ------------------------------------------------------------- */
    function initThreeBackground() {
        const canvas = document.getElementById('three-bg');
        if (!canvas) return;

        // Colors matching the warm peach / rose palette
        const colors = [0xc0605a, 0xe8a598, 0xf2c4a0, 0x9b59b6, 0xffa07a];

        let width = canvas.clientWidth;
        let height = canvas.clientHeight;

        // 1. Create Scene, Camera, and Renderer
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
        camera.position.z = 80;

        const renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: true
        });
        renderer.setSize(width, height, false);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // 2. Add Lights for dimension
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
        scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0xffffff, 0.85);
        pointLight.position.set(20, 40, 50);
        scene.add(pointLight);

        // 3. Create Heart Geometry using a 2D Shape
        const heartShape = new THREE.Shape();
        // Draw heart shape centered around origin (0, 0)
        // Values scaled down to fit comfortably in 3D scene
        heartShape.moveTo(0, 1.2);
        heartShape.bezierCurveTo(0, 1.2, 0.8, 2.6, 2.0, 2.6);
        heartShape.bezierCurveTo(3.5, 2.6, 4.4, 1.4, 4.4, -0.4);
        heartShape.bezierCurveTo(4.4, -2.6, 2.6, -4.8, 0, -7.0);
        heartShape.bezierCurveTo(-2.6, -4.8, -4.4, -2.6, -4.4, -0.4);
        heartShape.bezierCurveTo(-4.4, 1.4, -3.5, 2.6, -2.0, 2.6);
        heartShape.bezierCurveTo(-0.8, 2.6, 0, 1.2, 0, 1.2);

        // Extrude shape to make it a solid 3D heart
        const extrudeSettings = {
            depth: 0.8,
            bevelEnabled: true,
            bevelSegments: 4,
            steps: 1,
            bevelSize: 0.3,
            bevelThickness: 0.3
        };
        const geometry = new THREE.ExtrudeGeometry(heartShape, extrudeSettings);
        // Center the extruded geometry
        geometry.center();

        // 4. Populate Hearts
        const heartCount = 35;
        const hearts = [];

        for (let i = 0; i < heartCount; i++) {
            // Material with random warm color and soft transparency
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            const material = new THREE.MeshLambertMaterial({
                color: randomColor,
                transparent: true,
                opacity: THREE.MathUtils.randFloat(0.18, 0.45),
                roughness: 0.4,
                metalness: 0.1
            });

            const mesh = new THREE.Mesh(geometry, material);

            // Random scale
            const scale = THREE.MathUtils.randFloat(0.4, 1.4);
            mesh.scale.set(scale, scale, scale);

            // Random position in 3D coordinate space
            mesh.position.set(
                THREE.MathUtils.randFloatSpread(100), // x
                THREE.MathUtils.randFloatSpread(90),  // y
                THREE.MathUtils.randFloat(-100, 20)   // z (depth)
            );

            // Random rotation speed and direction
            mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
            
            // Custom physics properties for physics simulation in render loop
            mesh.userData = {
                speedY: THREE.MathUtils.randFloat(0.04, 0.12),
                speedX: THREE.MathUtils.randFloat(0.01, 0.05),
                rotX: THREE.MathUtils.randFloat(0.002, 0.01),
                rotY: THREE.MathUtils.randFloat(0.002, 0.01),
                swayAmplitude: THREE.MathUtils.randFloat(0.05, 0.2),
                swaySpeed: THREE.MathUtils.randFloat(0.5, 1.5),
                time: Math.random() * 100
            };

            scene.add(mesh);
            hearts.push(mesh);
        }

        // 5. Mouse Interaction variables
        let mouseX = 0;
        let mouseY = 0;
        let targetX = 0;
        let targetY = 0;

        window.addEventListener('mousemove', (e) => {
            // Normalize mouse coordinates in [-1, 1] range
            mouseX = (e.clientX / window.innerWidth) - 0.5;
            mouseY = (e.clientY / window.innerHeight) - 0.5;
        });

        // 6. Resize Handler
        function onWindowResize() {
            width = canvas.clientWidth;
            height = canvas.clientHeight;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height, false);
        }
        window.addEventListener('resize', onWindowResize);

        // 7. Anim Loop
        function animate(timestamp) {
            requestAnimationFrame(animate);

            // Smoothly interpolate camera position towards mouse targets
            targetX += (mouseX - targetX) * 0.06;
            targetY += (mouseY - targetY) * 0.06;

            camera.position.x = targetX * 35;
            camera.position.y = -targetY * 35;
            camera.lookAt(scene.position);

            // Animate each heart
            hearts.forEach((heart) => {
                const u = heart.userData;
                u.time += 0.01;

                // Drift upward
                heart.position.y += u.speedY;
                
                // Horizontal drift (sway) using sine wave
                heart.position.x += Math.sin(u.time * u.swaySpeed) * u.swayAmplitude;

                // Rotations
                heart.rotation.x += u.rotX;
                heart.rotation.y += u.rotY;

                // Reset position to bottom if it floats out of bounds
                if (heart.position.y > 60) {
                    heart.position.y = -60;
                    heart.position.x = THREE.MathUtils.randFloatSpread(100);
                }
            });

            renderer.render(scene, camera);
        }

        requestAnimationFrame(animate);
    }

    /* -------------------------------------------------------------
       SplitType Text Reveals & ScrollTrigger animations
       ------------------------------------------------------------- */
    function initScrollAnimations() {
        // Register ScrollTrigger plugin in GSAP
        gsap.registerPlugin(ScrollTrigger);

        // A. Heading Split Reveal Animations
        const splitTextElements = document.querySelectorAll('.split-text');
        splitTextElements.forEach((el) => {
            const split = new SplitType(el, { types: 'chars, words' });
            
            // Animation configs
            gsap.from(split.chars, {
                scrollTrigger: {
                    trigger: el,
                    start: "top 88%",
                    toggleActions: "play none none none"
                },
                opacity: 0,
                y: 35,
                rotateX: -65,
                stagger: 0.02,
                duration: 0.9,
                ease: "power4.out",
                // Clean up SplitType elements after animation completes for accessibility and screen reader support
                onComplete: () => {
                    split.revert();
                }
            });
        });

        // B. Teaser Grid Stagger Reveal
        const teaserGrid = document.querySelector('.teaser-grid');
        if (teaserGrid) {
            gsap.from('.teaser-card', {
                scrollTrigger: {
                    trigger: teaserGrid,
                    start: "top 80%",
                    toggleActions: "play none none none"
                },
                opacity: 0,
                y: 60,
                scale: 0.94,
                stagger: 0.15,
                duration: 0.9,
                ease: "back.out(1.3)"
            });
        }

        // C. Parallax Background Scroll on Quote Section
        const parallaxBg = document.querySelector('.quote-parallax-bg');
        if (parallaxBg) {
            gsap.to(parallaxBg, {
                scrollTrigger: {
                    trigger: '.quote-parallax-section',
                    start: "top bottom",
                    end: "bottom top",
                    scrub: true
                },
                yPercent: 20, // Parallax scroll translation percentage
                ease: "none"
            });
        }

        // D. Journey Visual Card pulse-scaling on scroll
        const visualCard = document.querySelector('.journey-card-visual');
        if (visualCard) {
            gsap.from(visualCard, {
                scrollTrigger: {
                    trigger: '.journey-section',
                    start: "top 75%",
                    toggleActions: "play none none none"
                },
                scale: 0.7,
                opacity: 0,
                duration: 1.2,
                ease: "elastic.out(1, 0.75)"
            });
        }
    }

    /* -------------------------------------------------------------
       Bootstrap Load
       ------------------------------------------------------------- */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initThreeBackground();
            initScrollAnimations();
        });
    } else {
        initThreeBackground();
        initScrollAnimations();
    }

})();
