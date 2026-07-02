"""
Integration tests for the gallery page and bookflip.js functionality.
Task 6.3: Verify bookflip.js works correctly with gallery view.
"""
from django.test import TestCase
from django.urls import reverse

from memories.models import Memory, SiteSettings


class BookFlipGalleryIntegrationTests(TestCase):
    """
    Integration tests for the gallery page with bookflip navigation.
    Requirements 1.1, 1.2, 1.3
    """

    def setUp(self):
        """Create test memories for gallery testing."""
        # Create site settings
        SiteSettings.objects.get_or_create(pk=1)
        
        # Create test memories
        self.memory1 = Memory.objects.create(
            caption='First memory',
            display_order=1,
            alt_text='First photo',
        )
        self.memory1.photo.name = 'memories/test1.jpg'
        self.memory1.save_base(update_fields=['photo'])

        self.memory2 = Memory.objects.create(
            caption='Second memory',
            display_order=2,
            alt_text='Second photo',
        )
        self.memory2.photo.name = 'memories/test2.jpg'
        self.memory2.save_base(update_fields=['photo'])

        self.memory3 = Memory.objects.create(
            caption='Third memory',
            display_order=3,
            alt_text='Third photo',
        )
        self.memory3.photo.name = 'memories/test3.jpg'
        self.memory3.save_base(update_fields=['photo'])

    def test_gallery_view_returns_200(self):
        """Gallery page loads successfully."""
        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)

    def test_gallery_context_contains_pages(self):
        """Gallery view groups memories into pages correctly."""
        response = self.client.get(reverse('gallery'))
        self.assertIn('pages', response.context)
        pages = response.context['pages']
        
        # 3 memories should create 2 pages (2 memories on page 1, 1 on page 2)
        self.assertEqual(len(pages), 2)
        self.assertEqual(len(pages[0]), 2)  # First page has 2 memories
        self.assertEqual(len(pages[1]), 1)  # Second page has 1 memory

    def test_gallery_context_contains_memories_json(self):
        """Gallery view includes JSON-serialized memories for JS."""
        response = self.client.get(reverse('gallery'))
        self.assertIn('memories_json', response.context)
        
        import json
        memories_data = json.loads(response.context['memories_json'])
        
        # Should have 3 memories
        self.assertEqual(len(memories_data), 3)
        
        # Verify structure of first memory
        self.assertIn('id', memories_data[0])
        self.assertIn('photo_url', memories_data[0])
        self.assertIn('caption', memories_data[0])
        self.assertIn('date', memories_data[0])
        self.assertIn('alt_text', memories_data[0])
        self.assertIn('display_order', memories_data[0])

    def test_gallery_template_includes_bookflip_js(self):
        """Gallery template loads bookflip.js script."""
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'bookflip')

    def test_gallery_template_includes_memories_data_script(self):
        """Gallery template includes memories-data JSON script element."""
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'id="memories-data"')

    def test_gallery_template_has_navigation_controls(self):
        """Gallery template includes next/prev navigation buttons."""
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'id="btn-prev"')
        self.assertContains(response, 'id="btn-next"')
        self.assertContains(response, 'id="current-page"')
        self.assertContains(response, 'id="total-pages"')

    def test_gallery_template_has_book_container(self):
        """Gallery template includes book-container for page spreads."""
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'id="book-container"')

    def test_gallery_page_spreads_match_pages_context(self):
        """Number of page-spread elements matches pages in context."""
        response = self.client.get(reverse('gallery'))
        pages_count = len(response.context['pages'])
        
        # Count page-spread elements in HTML
        html_content = response.content.decode('utf-8')
        spread_count = html_content.count('class="page-spread')
        
        self.assertEqual(spread_count, pages_count)

    def test_gallery_first_spread_is_active(self):
        """First page spread has 'active' class applied."""
        response = self.client.get(reverse('gallery'))
        html_content = response.content.decode('utf-8')
        
        # First spread should have 'active' class
        self.assertIn('class="page-spread active"', html_content)

    def test_gallery_memories_ordered_by_display_order(self):
        """Memories appear in correct order based on display_order field."""
        response = self.client.get(reverse('gallery'))
        pages = response.context['pages']
        
        # Flatten pages to get all memories in order
        all_memories = [m for page in pages for m in page]
        
        # Verify order
        self.assertEqual(all_memories[0].caption, 'First memory')
        self.assertEqual(all_memories[1].caption, 'Second memory')
        self.assertEqual(all_memories[2].caption, 'Third memory')

    def test_empty_gallery_shows_empty_state(self):
        """Gallery with no memories shows empty state message."""
        Memory.objects.all().delete()
        
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'No memories have been added yet')

    def test_gallery_with_single_memory(self):
        """Gallery with single memory creates one page with blank right panel."""
        Memory.objects.all().delete()
        
        memory = Memory.objects.create(
            caption='Only memory',
            display_order=1,
            alt_text='Only photo',
        )
        memory.photo.name = 'memories/only.jpg'
        memory.save_base(update_fields=['photo'])
        
        response = self.client.get(reverse('gallery'))
        pages = response.context['pages']
        
        self.assertEqual(len(pages), 1)
        self.assertEqual(len(pages[0]), 1)
        
        # Should have page-blank class for right panel
        self.assertContains(response, 'page-blank')

    def test_gallery_template_has_animation_selector(self):
        """Gallery template includes animation type toggle buttons."""
        response = self.client.get(reverse('gallery'))
        html = response.content.decode('utf-8')

        # Animation selector group
        self.assertIn('anim-selector', html)

        # Both mode buttons present
        self.assertIn('data-mode="book"', html)
        self.assertIn('data-mode="fade"', html)

    def test_gallery_book_mode_active_by_default(self):
        """Book Flip button is active (btn-anim--active) by default on page load."""
        response = self.client.get(reverse('gallery'))
        html = response.content.decode('utf-8')

        # Book button carries the active class; fade button does not
        self.assertIn('data-mode="book"', html)
        # The book button element should contain btn-anim--active
        book_btn_idx = html.find('data-mode="book"')
        # Search back a bit for the class attribute on that button
        snippet = html[max(0, book_btn_idx - 100):book_btn_idx + 50]
        self.assertIn('btn-anim--active', snippet)

    def test_gallery_template_has_fade_wrapper(self):
        """Gallery template includes the fade-gallery-wrapper element."""
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'id="fade-gallery-wrapper"')
        self.assertContains(response, 'id="fade-cards-container"')



class CaptionAndDateDisplayTests(TestCase):
    """
    Tests verifying caption text and date are displayed alongside photos in the
    gallery — all three animation modes (book-flip HTML, fade-in via JSON,
    carousel via JSON).

    Validates: Requirement 2.3 — WHEN the Visitor views a Memory in the gallery,
    THE Website SHALL display the caption and date (if present) alongside the photo.
    """

    def setUp(self):
        SiteSettings.objects.get_or_create(pk=1)

        import datetime

        # Memory with caption AND date — goes on left page of spread 1
        self.memory_with_date = Memory.objects.create(
            caption='A sunny afternoon',
            date=datetime.date(2023, 6, 15),
            display_order=1,
            alt_text='Photo one',
        )
        self.memory_with_date.photo.name = 'memories/cap_test1.jpg'
        self.memory_with_date.save_base(update_fields=['photo'])

        # Memory with caption but NO date — goes on right page of spread 1
        self.memory_no_date = Memory.objects.create(
            caption='A rainy evening',
            date=None,
            display_order=2,
            alt_text='Photo two',
        )
        self.memory_no_date.photo.name = 'memories/cap_test2.jpg'
        self.memory_no_date.save_base(update_fields=['photo'])

    # ------------------------------------------------------------------
    # Book-flip mode (server-rendered HTML)
    # ------------------------------------------------------------------

    def test_book_flip_html_contains_caption_text(self):
        """Gallery HTML (book-flip page panels) renders caption text."""
        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A sunny afternoon')
        self.assertContains(response, 'A rainy evening')

    def test_book_flip_html_contains_date_in_time_element(self):
        """Gallery HTML renders the date inside a <time> element for memories that have a date."""
        response = self.client.get(reverse('gallery'))
        html = response.content.decode('utf-8')

        # The date field should appear as a datetime attribute on a <time> tag
        self.assertIn('datetime="2023-06-15"', html)
        # The human-readable date should also be present
        self.assertIn('June 15, 2023', html)

    def test_book_flip_html_omits_time_element_when_no_date(self):
        """Gallery HTML does not render a <time> element for memories without a date."""
        response = self.client.get(reverse('gallery'))
        html = response.content.decode('utf-8')

        # The no-date memory caption should still appear
        self.assertIn('A rainy evening', html)
        # Only one datetime attribute should be present (for memory_with_date)
        self.assertEqual(html.count('datetime="'), 1)

    def test_book_flip_both_left_and_right_page_captions_rendered(self):
        """Both left and right page panels in book-flip mode render their captions."""
        response = self.client.get(reverse('gallery'))
        html = response.content.decode('utf-8')

        # Both memories share spread 1, so both captions must appear inside
        # .page-caption elements.  We verify the caption-text class is present
        # at least twice (once per panel).
        self.assertGreaterEqual(html.count('caption-text'), 2)

    # ------------------------------------------------------------------
    # JSON payload (used by fade-in and carousel modes)
    # ------------------------------------------------------------------

    def test_memories_json_contains_caption_and_date(self):
        """memories_json context includes caption and date for each memory."""
        import json
        response = self.client.get(reverse('gallery'))
        memories_data = json.loads(response.context['memories_json'])

        captions = [m['caption'] for m in memories_data]
        self.assertIn('A sunny afternoon', captions)
        self.assertIn('A rainy evening', captions)

        # The memory with a date should have a non-empty date string
        dated = next(m for m in memories_data if m['caption'] == 'A sunny afternoon')
        self.assertEqual(dated['date'], '2023-06-15')

        # The memory without a date should have an empty date string
        undated = next(m for m in memories_data if m['caption'] == 'A rainy evening')
        self.assertEqual(undated['date'], '')


class CarouselModeTests(TestCase):
    """
    Tests for carousel animation mode (task 6.5).
    Requirement 1.5 — Gallery SHALL support at least two additional animation
    types beyond book-style (fade-in is the second; carousel is the third).
    """

    def setUp(self):
        SiteSettings.objects.get_or_create(pk=1)
        memory = Memory.objects.create(
            caption='Carousel test memory',
            display_order=1,
            alt_text='Carousel photo',
        )
        memory.photo.name = 'memories/carousel_test.jpg'
        memory.save_base(update_fields=['photo'])

    def test_carousel_mode_button_present(self):
        """Gallery HTML includes a data-mode="carousel" button."""
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'data-mode="carousel"')

    def test_carousel_wrapper_present(self):
        """Gallery HTML includes the carousel-wrapper element."""
        response = self.client.get(reverse('gallery'))
        self.assertContains(response, 'carousel-wrapper')


class PlaceholderFallbackTests(TestCase):
    """
    Tests for onerror / fallback-src on gallery img elements.
    Requirement 1.7 — IF a photo fails to load, THEN the Website SHALL display
    a styled placeholder image in place of the missing photo.
    """

    def setUp(self):
        SiteSettings.objects.get_or_create(pk=1)
        for i in range(1, 3):
            memory = Memory.objects.create(
                caption=f'Fallback memory {i}',
                display_order=i,
                alt_text=f'Fallback photo {i}',
            )
            memory.photo.name = f'memories/fallback_test{i}.jpg'
            memory.save_base(update_fields=['photo'])

    def test_gallery_img_tags_have_onerror_or_fallback_src(self):
        """
        Every <img> tag in the gallery HTML must carry either an onerror
        attribute (inline handler) or a data-fallback-src attribute
        (used by a JS addEventListener error handler) so that broken images
        are replaced with the placeholder SVG.

        Validates: Requirement 1.7
        """
        from html.parser import HTMLParser

        class ImgParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.img_count = 0
                self.fallback_count = 0
                self.missing_fallback = []

            def handle_starttag(self, tag, attrs):
                if tag == 'img':
                    self.img_count += 1
                    attrs_dict = dict(attrs)
                    has_onerror = 'onerror' in attrs_dict
                    has_fallback_src = 'data-fallback-src' in attrs_dict
                    if has_onerror or has_fallback_src:
                        self.fallback_count += 1
                    else:
                        self.missing_fallback.append(attrs_dict.get('src', '<no src>'))

        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)

        parser = ImgParser()
        parser.feed(response.content.decode('utf-8'))

        self.assertGreater(parser.img_count, 0, "Expected at least one <img> tag in the gallery HTML")
        self.assertEqual(
            parser.img_count,
            parser.fallback_count,
            f"Some <img> tags are missing onerror/data-fallback-src: {parser.missing_fallback}",
        )


class LazyLoadingTests(TestCase):
    """
    Tests for lazy-loading on gallery img elements.
    Requirement 7.2 — The Website SHALL lazy-load photos outside the current viewport.
    """

    def setUp(self):
        SiteSettings.objects.get_or_create(pk=1)
        for i in range(1, 4):
            memory = Memory.objects.create(
                caption=f'Memory {i}',
                display_order=i,
                alt_text=f'Photo {i}',
            )
            memory.photo.name = f'memories/lazy_test{i}.jpg'
            memory.save_base(update_fields=['photo'])

    def test_all_img_tags_have_loading_lazy(self):
        """All <img> tags rendered in the gallery response include loading="lazy"."""
        from html.parser import HTMLParser

        class ImgParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.img_count = 0
                self.lazy_count = 0

            def handle_starttag(self, tag, attrs):
                if tag == 'img':
                    self.img_count += 1
                    attrs_dict = dict(attrs)
                    if attrs_dict.get('loading') == 'lazy':
                        self.lazy_count += 1

        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)

        parser = ImgParser()
        parser.feed(response.content.decode('utf-8'))

        self.assertGreater(parser.img_count, 0, "Expected at least one <img> tag in the gallery HTML")
        self.assertEqual(
            parser.img_count,
            parser.lazy_count,
            f"Not all <img> tags have loading=\"lazy\": "
            f"{parser.lazy_count}/{parser.img_count} have it",
        )
