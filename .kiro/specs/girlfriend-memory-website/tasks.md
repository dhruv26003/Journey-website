# Tasks

## Task List

- [x] 1 Project Bootstrap
  - [x] 1.1 Create Django project and core app
  - [x] 1.2 Configure settings with environment variables
  - [x] 1.3 Add requirements.txt with pinned dependencies
  - [x] 1.4 Create .env.example file

- [x] 2 Data Models and Utilities
  - [x] 2.1 Implement Memory model with all required fields
  - [x] 2.2 Implement SiteSettings singleton model
  - [x] 2.3 Implement compress_image utility (Pillow)
  - [x] 2.4 Implement validate_image_extension validator
  - [x] 2.5 Wire compression into Memory.save()
  - [x] 2.6 Run and apply initial migrations

- [x] 3 Django Admin Configuration
  - [x] 3.1 Register Memory in admin with list_editable display_order
  - [x] 3.2 Register SiteSettings in admin (singleton guard — no add/delete)
  - [x] 3.3 Verify admin upload, edit, delete flows manually

- [x] 4 Base Template and Static Setup
  - [x] 4.1 Create base.html with Bootstrap 5, nav links, block regions
  - [x] 4.2 Create main.css with warm color theme and font pairing
  - [x] 4.3 Configure STATIC_ROOT, STATICFILES_DIRS, and MEDIA settings
  - [x] 4.4 Add visible focus indicators to interactive elements in CSS

- [x] 5 Home / Landing Page
  - [x] 5.1 Implement HomeView querying SiteSettings and Memory
  - [x] 5.2 Create home.html with full-screen hero and navigation links
  - [x] 5.3 Implement hero slideshow (CSS transition auto-advance)
  - [x] 5.4 Implement typewriter animation for hero heading in main.js
  - [x] 5.5 Display welcome_message from SiteSettings in hero section

- [x] 6 Gallery Page with Animations
  - [x] 6.1 Implement GalleryView grouping memories into book pages
  - [x] 6.2 Create gallery.html with book-flip container and page panels
  - [x] 6.3 Implement bookflip.js (3-D CSS perspective transform, next/prev controls)
  - [x] 6.4 Add fade-in animation type as second gallery animation option
  - [x] 6.5 Add carousel slide animation type as third gallery animation option
  - [x] 6.6 Implement lazy-loading on all gallery <img> elements (loading="lazy")
  - [x] 6.7 Implement onerror placeholder handler for broken images in JS
  - [x] 6.8 Display caption and date alongside each photo in gallery layout

- [x] 7 Apology Page
  - [x] 7.1 Implement ApologyView querying SiteSettings for apology_message
  - [x] 7.2 Create apology.html with elegant typographic layout
  - [x] 7.3 Implement fade-in / slide-up entrance animation for message content
  - [x] 7.4 Implement apology.js for floating petal/heart decorative background
  - [x] 7.5 Respect prefers-reduced-motion media query in apology.js

- [x] 8 Accessibility and Responsive Design
  - [x] 8.1 Add alt_text field to all Memory <img> tags in templates
  - [x] 8.2 Verify Bootstrap 5 grid renders correctly at 320px, 768px, 1024px viewports
  - [x] 8.3 Run axe accessibility scan and fix reported violations
  - [x] 8.4 Verify Lighthouse accessibility score ≥ 80 on all core pages

- [x] 9 Performance
  - [x] 9.1 Configure cache headers for static assets (WhiteNoise or Nginx config)
  - [x] 9.2 Verify compress_image is triggered and reduces oversized uploads

- [x] 10 Tests
  - [x] 10.1 Write unit tests for compress_image (below/at/above 2 MB threshold)
  - [x] 10.2 Write unit tests for _resize_to_fit dimension calculations
  - [x] 10.3 Write unit tests for validate_image_extension (valid and invalid extensions)
  - [x] 10.4 Write unit tests for SiteSettings.get() singleton behavior
  - [x] 10.5 Write property-based test for Property 1: image compression size bound
  - [x] 10.6 Write property-based test for Property 2: compression preserves image validity
  - [x] 10.7 Write property-based test for Property 3: caption length enforcement
  - [x] 10.8 Write property-based test for Property 4: file extension validation
  - [x] 10.9 Write property-based test for Property 5: SiteSettings singleton and content round-trip
  - [x] 10.10 Write property-based test for Property 6: Memory display order preserved on retrieval
  - [x] 10.11 Write property-based test for Property 7: rendered memory contains required fields
  - [x] 10.12 Write integration tests for admin upload flow (valid and invalid files)
  - [x] 10.13 Write integration tests for gallery, apology, and home views

- [x] 11 Deployment Readiness
  - [x] 11.1 Create .env.example with all required environment variable keys
  - [x] 11.2 Document collectstatic and migration steps in README
  - [x] 11.3 Verify DEBUG=False configuration serves static files from STATIC_ROOT
  - [x] 11.4 Verify DATABASE_URL switches to PostgreSQL when set
