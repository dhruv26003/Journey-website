// bookflip.js — Gallery animation controller
// Supports three animation modes: "book", "fade", "carousel"
// Reads memories JSON injected by Django and drives next/prev navigation.

(function () {
    'use strict';

    /* ------------------------------------------------------------------
       DOM references — shared between modes
    ------------------------------------------------------------------ */
    const bookContainer  = document.getElementById('book-container');
    const fadeWrapper    = document.getElementById('fade-gallery-wrapper');
    const carouselWrapper = document.getElementById('carousel-wrapper');
    const btnPrev        = document.getElementById('btn-prev');
    const btnNext        = document.getElementById('btn-next');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan  = document.getElementById('total-pages');
    const animBtns       = document.querySelectorAll('.btn-anim');

    if (!bookContainer && !fadeWrapper && !carouselWrapper) return;

    /* ------------------------------------------------------------------
       Read memories JSON (rendered by Django template)
    ------------------------------------------------------------------ */
    const memoriesDataEl = document.getElementById('memories-data');
    let memoriesData = [];
    if (memoriesDataEl) {
        try {
            let data = JSON.parse(memoriesDataEl.textContent);
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }
            memoriesData = Array.isArray(data) ? data : [];
        } catch (err) {
            console.error('Failed to parse memories JSON:', err);
        }
    }

    /* ------------------------------------------------------------------
       Book-flip mode — spreads in DOM
    ------------------------------------------------------------------ */
    const spreads     = bookContainer ? Array.from(bookContainer.querySelectorAll('.page-spread')) : [];
    const totalSpreads = spreads.length;

    /* ------------------------------------------------------------------
       Current mode and index
    ------------------------------------------------------------------ */
    let currentMode  = 'book';
    let currentIndex = 0;
    let lastDelta    = 1;

    /* ------------------------------------------------------------------
       Shared UI helpers
    ------------------------------------------------------------------ */
    function updateNav() {
        const total   = currentMode === 'book' ? totalSpreads : memoriesData.length;
        const isFirst = currentIndex === 0;
        const isLast  = currentIndex >= total - 1;

        if (currentPageSpan) currentPageSpan.textContent = String(currentIndex + 1);
        if (totalPagesSpan)  totalPagesSpan.textContent  = String(total);
        if (btnPrev) btnPrev.disabled = isFirst;
        if (btnNext) btnNext.disabled = isLast;
    }

    /* ------------------------------------------------------------------
       Book-flip navigation — CSS class animation
    ------------------------------------------------------------------ */
    const ANIM_DURATION = 650; // ms — must match CSS animation duration
    let bookAnimating = false;

    function showSpread(index) {
        if (index < 0 || index >= totalSpreads || bookAnimating) return;
        bookAnimating = true;

        const prevIndex = currentIndex;
        currentIndex = index;

        const prevSpread = spreads[prevIndex];
        const nextSpread = spreads[index];

        // Outgoing
        if (prevSpread && prevSpread !== nextSpread) {
            const outClass = lastDelta > 0 ? 'flip-out-fwd' : 'flip-out-back';
            prevSpread.classList.add(outClass);
            setTimeout(() => {
                prevSpread.classList.remove('active', outClass);
            }, 360);
        }

        // Incoming
        const inClass = lastDelta > 0 ? 'flip-in-fwd' : 'flip-in-back';
        nextSpread.classList.add('active', inClass);
        setTimeout(() => {
            nextSpread.classList.remove(inClass);
            bookAnimating = false;
        }, ANIM_DURATION);

        updateNav();
    }

    /* ------------------------------------------------------------------
       Fade-in mode
    ------------------------------------------------------------------ */
    let fadeCards = [];
    let fadeBuilt = false;

    function buildFadeCards() {
        if (fadeBuilt || !fadeWrapper) return;
        fadeBuilt = true;

        const container = document.getElementById('fade-cards-container');
        if (!container) return;

        memoriesData.forEach((mem, i) => {
            const card = document.createElement('div');
            card.className = 'fade-card' + (i === 0 ? ' active' : '');
            card.setAttribute('data-index', String(i));
            card.setAttribute('role', 'group');
            card.setAttribute('aria-label', `Memory ${i + 1} of ${memoriesData.length}`);

            if (mem.is_video && mem.video_url) {
                const wrap = document.createElement('div');
                wrap.className = 'fade-card__video-wrap';
                const vid = document.createElement('video');
                vid.src = mem.video_url;
                vid.controls = true; vid.preload = 'metadata'; vid.loop = true;
                vid.className = 'fade-card__video';
                vid.setAttribute('aria-label', mem.alt_text || mem.caption);
                const badge = document.createElement('span');
                badge.className = 'media-type-badge'; badge.textContent = '🎥 Video';
                wrap.appendChild(vid); wrap.appendChild(badge);
                card.appendChild(wrap);
            } else if (mem.photo_url) {
                const wrap = document.createElement('div');
                wrap.className = 'fade-card__photo-wrap';
                const img = document.createElement('img');
                img.src = mem.photo_url;
                img.alt = mem.alt_text || mem.caption;
                img.loading = 'lazy';
                img.className = 'fade-card__photo';
                wrap.appendChild(img);
                card.appendChild(wrap);
            }

            const cap = document.createElement('div');
            cap.className = 'fade-card__caption';
            const txt = document.createElement('p');
            txt.className = 'fade-card__caption-text'; txt.textContent = mem.caption;
            cap.appendChild(txt);
            if (mem.date) {
                const t = document.createElement('time');
                t.className = 'fade-card__date'; t.setAttribute('datetime', mem.date);
                const d = new Date(mem.date + 'T00:00:00');
                t.textContent = d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
                cap.appendChild(t);
            }
            card.appendChild(cap);
            container.appendChild(card);
        });

        fadeCards = Array.from(container.querySelectorAll('.fade-card'));
    }

    function showFadeCard(index) {
        if (index < 0 || index >= fadeCards.length) return;
        fadeCards.forEach((card, i) => {
            card.classList.toggle('active', i === index);
        });
        currentIndex = index;
        updateNav();
    }

    /* ------------------------------------------------------------------
       Carousel mode
    ------------------------------------------------------------------ */
    let carouselBuilt = false;

    function buildCarousel() {
        if (carouselBuilt || !carouselWrapper) return;
        carouselBuilt = true;

        const track = document.getElementById('carousel-track');
        if (!track) return;

        memoriesData.forEach((mem, i) => {
            const item = document.createElement('div');
            item.className = 'carousel-item';
            item.setAttribute('data-index', String(i));
            item.setAttribute('role', 'group');
            item.setAttribute('aria-label', `Memory ${i + 1} of ${memoriesData.length}`);

            if (mem.is_video && mem.video_url) {
                const wrap = document.createElement('div');
                wrap.className = 'carousel-item__video-wrap';
                const vid = document.createElement('video');
                vid.src = mem.video_url;
                vid.controls = true; vid.preload = 'metadata'; vid.loop = true;
                vid.className = 'carousel-item__video';
                const badge = document.createElement('span');
                badge.className = 'media-type-badge'; badge.textContent = '🎥 Video';
                wrap.appendChild(vid); wrap.appendChild(badge);
                item.appendChild(wrap);
            } else if (mem.photo_url) {
                const wrap = document.createElement('div');
                wrap.className = 'carousel-item__photo-wrap';
                const img = document.createElement('img');
                img.src = mem.photo_url;
                img.alt = mem.alt_text || mem.caption;
                img.loading = 'lazy';
                img.className = 'carousel-item__photo';
                wrap.appendChild(img);
                item.appendChild(wrap);
            }

            const cap = document.createElement('div');
            cap.className = 'carousel-item__caption';
            const txt = document.createElement('p');
            txt.className = 'carousel-item__caption-text'; txt.textContent = mem.caption;
            cap.appendChild(txt);
            if (mem.date) {
                const t = document.createElement('time');
                t.className = 'carousel-item__date'; t.setAttribute('datetime', mem.date);
                const d = new Date(mem.date + 'T00:00:00');
                t.textContent = d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
                cap.appendChild(t);
            }
            item.appendChild(cap);
            track.appendChild(item);
        });
    }

    function showCarouselItem(index) {
        if (index < 0 || index >= memoriesData.length) return;
        const track = document.getElementById('carousel-track');
        if (track) {
            track.style.transform = `translateX(${-index * 100}%)`;
        }
        currentIndex = index;
        updateNav();
    }

    /* ------------------------------------------------------------------
       Generic navigate
    ------------------------------------------------------------------ */
    function navigate(delta) {
        const next = currentIndex + delta;
        lastDelta = delta;
        if (currentMode === 'book') {
            showSpread(next);
        } else if (currentMode === 'fade') {
            showFadeCard(next);
        } else {
            showCarouselItem(next);
        }
    }

    /* ------------------------------------------------------------------
       Mode switching
    ------------------------------------------------------------------ */
    function activateMode(mode) {
        if (mode === currentMode) return;

        const bookWrapper = bookContainer ? bookContainer.closest('.book-flip-wrapper') : null;

        const modeWrappers = {
            'book':     bookWrapper,
            'fade':     fadeWrapper,
            'carousel': carouselWrapper
        };
        const modeDisplays = {
            'book':     'flex',
            'fade':     'flex',
            'carousel': 'flex'
        };

        const oldWrapper = modeWrappers[currentMode];
        const newWrapper = modeWrappers[mode];

        currentMode  = mode;
        currentIndex = 0;
        lastDelta    = 1;

        // Update toggle buttons
        animBtns.forEach(btn => {
            const isActive = btn.dataset.mode === mode;
            btn.classList.toggle('btn-anim--active', isActive);
            btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        // Hide old wrapper
        if (oldWrapper) {
            oldWrapper.style.setProperty('display', 'none', 'important');
            oldWrapper.classList.remove('active');
        }

        // Show new wrapper — set explicit display value
        if (newWrapper) {
            newWrapper.style.setProperty('display', modeDisplays[mode], 'important');
            newWrapper.classList.add('active');

            if (mode === 'book') {
                showSpread(0);
            } else if (mode === 'fade') {
                buildFadeCards();
                showFadeCard(0);
            } else {
                buildCarousel();
                showCarouselItem(0);
            }
        }
    }

    // Wire up selector buttons
    animBtns.forEach(btn => {
        btn.addEventListener('click', () => activateMode(btn.dataset.mode));
    });

    /* ------------------------------------------------------------------
       Next / Prev buttons
    ------------------------------------------------------------------ */
    if (btnNext) btnNext.addEventListener('click', () => navigate(1));
    if (btnPrev) btnPrev.addEventListener('click', () => navigate(-1));

    /* ------------------------------------------------------------------
       Keyboard navigation
    ------------------------------------------------------------------ */
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') { e.preventDefault(); navigate(1); }
        else if (e.key === 'ArrowLeft') { e.preventDefault(); navigate(-1); }
    });

    /* ------------------------------------------------------------------
       Touch / swipe navigation
    ------------------------------------------------------------------ */
    const swipeThreshold = 50;
    let touchStartX = 0;

    function addSwipe(el) {
        if (!el) return;
        el.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        el.addEventListener('touchend', (e) => {
            const dist = e.changedTouches[0].screenX - touchStartX;
            if (dist < -swipeThreshold) navigate(1);
            else if (dist > swipeThreshold) navigate(-1);
        }, { passive: true });
    }

    if (bookContainer) addSwipe(bookContainer);
    if (fadeWrapper)   addSwipe(fadeWrapper);
    if (carouselWrapper) addSwipe(carouselWrapper);

    /* ------------------------------------------------------------------
       Initialise — show first spread immediately
    ------------------------------------------------------------------ */
    // Make sure first spread is active
    if (spreads.length > 0) {
        spreads[0].classList.add('active');
    }
    updateNav();

    console.log('Gallery initialised — mode:', currentMode, '| memories:', memoriesData.length, '| spreads:', totalSpreads);
})();
