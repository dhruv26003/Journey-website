# Requirements Document

## Introduction

A personal memory and tribute website built with Django to celebrate and preserve shared memories between two people. The site features an animated photo gallery with book-style and other visually rich animations, a heartfelt apology page, and a curated memories section — all designed to evoke nostalgia and warmth when the visitor browses through it. The site is intended for a single visitor (Ana) and managed by a single owner (the creator).

## Glossary

- **Website**: The Django-based tribute web application described in this document
- **Owner**: The person who created and manages the website (the user, "Mara")
- **Visitor**: The intended recipient of the website (Ana)
- **Photo**: An image uploaded and displayed on the website
- **Gallery**: The collection of photos displayed with animations
- **Book Animation**: A page-flip style animation that simulates turning pages of a photo book
- **Memory**: A photo paired with a caption and optional date, representing a shared moment
- **Apology Page**: A dedicated page containing a personal written apology message from the Owner to the Visitor
- **Admin Panel**: Django's built-in admin interface used by the Owner to manage content
- **Media Files**: User-uploaded photos stored on the server

---

## Requirements

### Requirement 1: Photo Gallery with Book-Style Animation

**User Story:** As the Owner, I want to display our photos in a beautiful animated photo book, so that the Visitor can relive our shared memories in an engaging and emotional way.

#### Acceptance Criteria

1. THE Website SHALL display a photo gallery page accessible from the main navigation.
2. WHEN the Visitor navigates to the gallery, THE Website SHALL render photos in a book-style page-flip animation using CSS and/or JavaScript.
3. WHEN the Visitor clicks or taps the "next page" control, THE Website SHALL animate the transition to the next photo or set of photos using a realistic page-turn effect.
4. WHEN the Visitor clicks or taps the "previous page" control, THE Website SHALL animate the transition to the previous photo or set of photos.
5. THE Gallery SHALL support at least two additional animation types beyond book-style (e.g., fade-in, zoom, carousel slide) selectable per gallery section.
6. WHEN a photo finishes loading, THE Website SHALL display the photo at full quality without distortion or cropping of faces.
7. IF a photo fails to load, THEN THE Website SHALL display a styled placeholder image in place of the missing photo.
8. THE Gallery SHALL be fully responsive and render correctly on screen widths from 320px to 1920px using Bootstrap's grid system.

---

### Requirement 2: Memory Cards with Captions

**User Story:** As the Owner, I want each photo to have a caption and optional date, so that the Visitor understands the story and context behind each memory.

#### Acceptance Criteria

1. THE Website SHALL associate each Photo with a text caption of up to 300 characters.
2. THE Website SHALL associate each Photo with an optional date field indicating when the memory occurred.
3. WHEN the Visitor views a Memory in the gallery, THE Website SHALL display the caption and date (if present) alongside the photo.
4. WHEN the caption text exceeds 100 characters in a card layout, THE Website SHALL display the full caption text on hover or tap without truncation.
5. THE Memory model in Django SHALL store the photo file path, caption, date, and display order as distinct fields.

---

### Requirement 3: Apology Page

**User Story:** As the Owner, I want a dedicated apology page with a personal message, so that the Visitor can read a heartfelt apology and feel the sincerity of my words.

#### Acceptance Criteria

1. THE Website SHALL include a dedicated Apology page accessible from the main navigation.
2. THE Apology Page SHALL display the Owner's apology message in a visually distinct, elegant typographic layout.
3. THE Apology Page SHALL support formatted text including paragraphs, emphasis, and line breaks stored as HTML-safe content in the database.
4. WHEN the Visitor loads the Apology Page, THE Website SHALL display a soft animated entrance effect (e.g., fade-in or slide-up) for the message content.
5. THE Apology Page SHALL display a decorative visual element (e.g., animated floating petals, hearts, or soft bokeh effect) as a background to reinforce the emotional tone.
6. THE Owner SHALL be able to update the apology message text through the Django Admin Panel without modifying source code.

---

### Requirement 4: Home / Landing Page

**User Story:** As the Owner, I want a beautiful landing page that sets the emotional tone, so that the Visitor immediately feels welcomed and curious to explore.

#### Acceptance Criteria

1. THE Website SHALL display a landing (home) page as the default route (`/`).
2. THE Home Page SHALL display a full-screen hero section with a featured photo or looping background slideshow of shared memories.
3. WHEN the Home Page loads, THE Website SHALL animate the hero heading text using a typewriter or fade-in effect.
4. THE Home Page SHALL include navigation links to the Gallery page and the Apology page.
5. THE Home Page SHALL display a short welcome message configurable by the Owner via the Django Admin Panel.
6. THE Website SHALL apply a consistent color theme (soft, warm tones) and font pairing across all pages using Bootstrap and custom CSS.

---

### Requirement 5: Content Management via Django Admin

**User Story:** As the Owner, I want to manage all photos, captions, and page content through Django's admin panel, so that I can update the site without writing code.

#### Acceptance Criteria

1. THE Admin Panel SHALL allow the Owner to upload, edit, and delete Photos with their associated captions, dates, and display order.
2. THE Admin Panel SHALL allow the Owner to reorder Memory entries using a numeric order field.
3. THE Admin Panel SHALL allow the Owner to update the apology message text.
4. THE Admin Panel SHALL allow the Owner to update the home page welcome message.
5. WHEN the Owner uploads a Photo, THE Website SHALL store the file in the configured `MEDIA_ROOT` directory and serve it via the `MEDIA_URL` path.
6. IF an uploaded file is not a valid image format (JPEG, PNG, GIF, or WebP), THEN THE Admin Panel SHALL reject the upload and display a descriptive validation error.

---

### Requirement 6: Responsive Design and Accessibility

**User Story:** As the Visitor, I want the website to look beautiful and work correctly on my phone or laptop, so that I can browse memories comfortably on any device.

#### Acceptance Criteria

1. THE Website SHALL use Bootstrap 5 as the primary CSS framework for layout and responsiveness.
2. THE Website SHALL render all pages correctly on mobile (320px–767px), tablet (768px–1023px), and desktop (1024px+) viewports.
3. THE Website SHALL include descriptive `alt` text on every Photo element for screen reader accessibility.
4. THE Website SHALL achieve a Lighthouse accessibility score of 80 or above on all core pages.
5. WHEN the Visitor uses keyboard navigation, THE Website SHALL provide visible focus indicators on all interactive elements.

---

### Requirement 7: Site Performance

**User Story:** As the Visitor, I want the pages to load quickly, so that the experience feels smooth and the animations are not interrupted by slow loading.

#### Acceptance Criteria

1. THE Website SHALL serve all static assets (CSS, JS, images) with cache headers set to a minimum of 1 hour.
2. WHEN a Gallery page is loaded, THE Website SHALL lazy-load photos that are outside the current viewport to reduce initial page load time.
3. THE Website SHALL compress uploaded photos to a maximum file size of 2MB before storage while preserving visual quality.
4. IF a photo's original file size exceeds 2MB, THEN THE Website SHALL automatically resize and compress the image upon upload using Pillow.

---

### Requirement 8: Deployment and Environment Configuration

**User Story:** As the Owner, I want the website to run reliably on a server, so that the Visitor can access it at any time.

#### Acceptance Criteria

1. THE Website SHALL be built using Django (Python) as the backend web framework.
2. THE Website SHALL use environment variables for all sensitive configuration values (secret key, database URL, debug mode) via a `.env` file.
3. IF `DEBUG` is set to `False`, THEN THE Website SHALL serve static files from the configured `STATIC_ROOT` directory.
4. THE Website SHALL include a `requirements.txt` file listing all Python dependencies with pinned versions.
5. THE Website SHALL use SQLite as the default database for local development and support PostgreSQL as a production database via the `DATABASE_URL` environment variable.
