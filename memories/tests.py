import random
from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
from django.test import TestCase

from memories.utils import validate_image_extension


def _mock_file(name: str):
    """Return a mock object that mimics an uploaded file with the given filename."""
    f = MagicMock()
    f.name = name
    return f


class ValidateImageExtensionTests(TestCase):
    """Unit tests for validate_image_extension (Requirement 5.6)."""

    # --- Allowed extensions ---

    def test_accepts_jpg(self):
        validate_image_extension(_mock_file('photo.jpg'))

    def test_accepts_jpeg(self):
        validate_image_extension(_mock_file('photo.jpeg'))

    def test_accepts_png(self):
        validate_image_extension(_mock_file('image.png'))

    def test_accepts_gif(self):
        validate_image_extension(_mock_file('animation.gif'))

    def test_accepts_webp(self):
        validate_image_extension(_mock_file('picture.webp'))

    def test_accepts_uppercase_extension(self):
        """Case-insensitive: .JPG should be treated the same as .jpg."""
        validate_image_extension(_mock_file('photo.JPG'))

    def test_accepts_mixed_case_extension(self):
        validate_image_extension(_mock_file('photo.Jpeg'))

    # --- Rejected extensions ---

    def test_rejects_txt(self):
        with self.assertRaises(ValidationError):
            validate_image_extension(_mock_file('document.txt'))

    def test_rejects_pdf(self):
        with self.assertRaises(ValidationError):
            validate_image_extension(_mock_file('document.pdf'))

    def test_rejects_exe(self):
        with self.assertRaises(ValidationError):
            validate_image_extension(_mock_file('malware.exe'))

    def test_rejects_bmp(self):
        with self.assertRaises(ValidationError):
            validate_image_extension(_mock_file('image.bmp'))

    def test_rejects_tiff(self):
        with self.assertRaises(ValidationError):
            validate_image_extension(_mock_file('scan.tiff'))

    def test_rejects_no_extension(self):
        with self.assertRaises(ValidationError):
            validate_image_extension(_mock_file('noextension'))

    # --- Error message format ---

    def test_error_message_contains_extension(self):
        """The ValidationError message should include the invalid extension."""
        with self.assertRaises(ValidationError) as ctx:
            validate_image_extension(_mock_file('file.bmp'))
        self.assertIn('.bmp', str(ctx.exception))

    def test_error_message_contains_allowed_formats(self):
        """The ValidationError message should mention allowed formats."""
        with self.assertRaises(ValidationError) as ctx:
            validate_image_extension(_mock_file('file.txt'))
        msg = str(ctx.exception)
        self.assertIn('JPEG', msg)
        self.assertIn('PNG', msg)
        self.assertIn('GIF', msg)
        self.assertIn('WebP', msg)


# ---------------------------------------------------------------------------
# Integration tests — Admin upload, edit, delete flows (Requirements 5.1, 5.2)
# ---------------------------------------------------------------------------

import io

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from memories.admin import SiteSettingsAdmin
from memories.models import Memory, SiteSettings

User = get_user_model()


def _minimal_jpeg_bytes() -> bytes:
    """Return the raw bytes of a tiny valid JPEG (1×1 white pixel)."""
    from PIL import Image

    buf = io.BytesIO()
    img = Image.new('RGB', (1, 1), color=(255, 255, 255))
    img.save(buf, format='JPEG')
    return buf.getvalue()


class AdminMemoryFlowTests(TestCase):
    """
    Integration tests for the Memory admin upload, edit, and delete flows.
    Requirements 5.1, 5.2
    """

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpassword123',
            email='admin@test.com',
        )

    def setUp(self):
        self.client.force_login(self.superuser)

    # ------------------------------------------------------------------
    # 1. Upload flow
    # ------------------------------------------------------------------

    @override_settings(MEDIA_ROOT='/tmp/test_media_memories')
    def test_upload_valid_jpeg_returns_redirect(self):
        """
        POST a valid JPEG to the Memory admin add URL.
        Expect a 302 redirect (success), a Memory row in DB, and the file
        saved under MEDIA_ROOT.
        """
        import os
        add_url = reverse('admin:memories_memory_add')
        image_file = io.BytesIO(_minimal_jpeg_bytes())
        image_file.name = 'test_photo.jpg'

        memory_count_before = Memory.objects.count()

        response = self.client.post(
            add_url,
            data={
                'media_type': 'photo',
                'photo': image_file,
                'caption': 'A lovely day',
                'date': '2024-06-15',
                'display_order': '1',
                'alt_text': 'Us at the park',
                '_save': 'Save',
            },
        )
        # Django admin redirects to changelist on success
        self.assertIn(response.status_code, [301, 302],
                      msg='Expected a redirect after successful Memory upload.')

        # A new Memory row must have been created in the database
        self.assertEqual(
            Memory.objects.count(),
            memory_count_before + 1,
            msg='Expected one new Memory row in DB after valid JPEG upload.',
        )

        # The uploaded file must exist on disk under MEDIA_ROOT
        memory = Memory.objects.latest('uploaded_at')
        file_path = os.path.join('/tmp/test_media_memories', memory.photo.name)
        self.assertTrue(
            os.path.exists(file_path),
            msg=f'Expected uploaded file to exist at {file_path}',
        )

    # ------------------------------------------------------------------
    # 2. Edit flow
    # ------------------------------------------------------------------

    @override_settings(MEDIA_ROOT='/tmp/test_media_memories')
    def test_edit_existing_memory_returns_200(self):
        """
        GET the change URL of an existing Memory → HTTP 200.
        """
        # Create a Memory directly in DB (no file needed for GET)
        memory = Memory.objects.create(
            caption='Old caption',
            display_order=5,
        )
        # Assign a dummy photo path so the model is valid
        memory.photo.name = 'memories/dummy.jpg'
        memory.save_base(update_fields=['photo'])

        change_url = reverse('admin:memories_memory_change', args=[memory.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # 3. Delete flow
    # ------------------------------------------------------------------

    @override_settings(MEDIA_ROOT='/tmp/test_media_memories')
    def test_delete_memory_redirects(self):
        """
        POST to the Memory delete confirmation URL → redirect (success).
        """
        memory = Memory.objects.create(
            caption='To be deleted',
            display_order=10,
        )
        memory.photo.name = 'memories/dummy_delete.jpg'
        memory.save_base(update_fields=['photo'])

        delete_url = reverse('admin:memories_memory_delete', args=[memory.pk])
        response = self.client.post(delete_url, data={'post': 'yes'})
        self.assertIn(response.status_code, [301, 302],
                      msg='Expected a redirect after deleting a Memory.')
        self.assertFalse(Memory.objects.filter(pk=memory.pk).exists(),
                         msg='Memory should have been removed from the database.')

    # ------------------------------------------------------------------
    # 4. SiteSettings singleton guard — "Add" button hidden when row exists
    # ------------------------------------------------------------------

    def test_sitesettings_add_permission_denied_when_row_exists(self):
        """
        has_add_permission returns False when a SiteSettings row already exists.
        """
        SiteSettings.objects.get_or_create(pk=1)
        admin_instance = SiteSettingsAdmin(SiteSettings, AdminSite())

        # Simulate a plain request object; permission logic only checks DB.
        from django.test import RequestFactory
        request = RequestFactory().get('/')
        request.user = self.superuser

        self.assertFalse(
            admin_instance.has_add_permission(request),
            msg='has_add_permission should return False when a SiteSettings row exists.',
        )

    def test_sitesettings_add_permission_allowed_when_no_row(self):
        """
        has_add_permission returns True when no SiteSettings row exists yet.
        """
        SiteSettings.objects.all().delete()
        admin_instance = SiteSettingsAdmin(SiteSettings, AdminSite())

        from django.test import RequestFactory
        request = RequestFactory().get('/')
        request.user = self.superuser

        self.assertTrue(
            admin_instance.has_add_permission(request),
            msg='has_add_permission should return True when no SiteSettings row exists.',
        )

    # ------------------------------------------------------------------
    # 5. SiteSettings no-delete guard
    # ------------------------------------------------------------------

    def test_sitesettings_delete_permission_always_denied(self):
        """
        has_delete_permission always returns False for SiteSettings.
        """
        SiteSettings.objects.get_or_create(pk=1)
        admin_instance = SiteSettingsAdmin(SiteSettings, AdminSite())

        from django.test import RequestFactory
        request = RequestFactory().get('/')
        request.user = self.superuser

        # Without obj
        self.assertFalse(
            admin_instance.has_delete_permission(request),
            msg='has_delete_permission should return False (no obj).',
        )

        # With obj
        obj = SiteSettings.get()
        self.assertFalse(
            admin_instance.has_delete_permission(request, obj=obj),
            msg='has_delete_permission should return False (with obj).',
        )


# ---------------------------------------------------------------------------
# Integration tests — ApologyView (Requirement 3.1)
# ---------------------------------------------------------------------------

class ApologyViewTests(TestCase):
    """
    Integration tests for GET /apology/.
    Requirement 3.1 — The site SHALL include a dedicated Apology page
    accessible from the main navigation.
    """

    def test_apology_returns_200(self):
        """GET /apology/ returns HTTP 200."""
        response = self.client.get('/apology/')
        self.assertEqual(response.status_code, 200)

    def test_apology_message_in_context(self):
        """apology_message is present in the template context."""
        response = self.client.get('/apology/')
        self.assertIn('apology_message', response.context)

    def test_apology_message_reflects_site_settings(self):
        """The rendered page reflects the apology_message stored in SiteSettings."""
        settings = SiteSettings.get()
        settings.apology_message = '<p>I am truly sorry.</p>'
        settings.save()

        response = self.client.get('/apology/')
        self.assertContains(response, 'I am truly sorry.')


# ---------------------------------------------------------------------------
# Accessibility tests — alt_text on Memory <img> elements (Requirement 6.3)
# ---------------------------------------------------------------------------


class AltTextAccessibilityTests(TestCase):
    """
    Verify that Memory photo <img> elements on the home and gallery pages
    render with non-empty alt attributes (Requirement 6.3).
    """

    def _make_memory(self, caption='A sweet moment', alt_text='', display_order=1):
        """Create a Memory with a dummy photo path (no real file needed)."""
        memory = Memory.objects.create(
            caption=caption,
            alt_text=alt_text,
            display_order=display_order,
        )
        memory.photo.name = 'memories/dummy_alt_test.jpg'
        memory.save_base(update_fields=['photo'])
        return memory

    # ------------------------------------------------------------------
    # Home page — hero slideshow
    # ------------------------------------------------------------------

    def test_home_img_uses_alt_text_when_set(self):
        """
        Home page: when a Memory has alt_text, the rendered <img> contains
        that alt value.
        Validates: Requirement 6.3
        """
        self._make_memory(caption='Beach day', alt_text='Us playing on the beach')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alt="Us playing on the beach"')

    def test_home_img_falls_back_to_caption_when_alt_text_empty(self):
        """
        Home page: when alt_text is empty the rendered <img> falls back to
        the caption value as alt text.
        Validates: Requirement 6.3
        """
        self._make_memory(caption='Sunset walk', alt_text='')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alt="Sunset walk"')

    def test_home_img_alt_never_empty_for_memories_with_caption(self):
        """
        Home page: every Memory with a caption always produces a non-empty
        alt attribute — never alt="".
        Validates: Requirement 6.3
        """
        self._make_memory(caption='Picnic in the park', alt_text='')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # alt="" should not appear for memory images (they have captions)
        self.assertNotIn('alt=""', content)

    # ------------------------------------------------------------------
    # Gallery page — book-flip panels
    # ------------------------------------------------------------------

    def test_gallery_img_uses_alt_text_when_set(self):
        """
        Gallery page: when a Memory has alt_text, the left/right page panel
        <img> contains that alt value.
        Validates: Requirement 6.3
        """
        self._make_memory(caption='Mountain hike', alt_text='Hiking the summit together',
                          display_order=1)
        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alt="Hiking the summit together"')

    def test_gallery_img_falls_back_to_caption_when_alt_text_empty(self):
        """
        Gallery page: when alt_text is empty the rendered <img> uses the
        caption as alt text.
        Validates: Requirement 6.3
        """
        self._make_memory(caption='Coffee date', alt_text='', display_order=1)
        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alt="Coffee date"')

    def test_gallery_img_alt_never_empty_for_memories_with_caption(self):
        """
        Gallery page: every memory image panel has a non-empty alt attribute.
        Validates: Requirement 6.3
        """
        self._make_memory(caption='Rainy afternoon', alt_text='', display_order=1)
        self._make_memory(caption='Stargazing night', alt_text='', display_order=2)
        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Within the book-flip panels, no <img> should have an empty alt
        self.assertNotIn('alt=""', content)


# ---------------------------------------------------------------------------
# Responsive layout tests — viewport meta tag (Requirement 6.2)
# ---------------------------------------------------------------------------


class ViewportMetaTagTests(TestCase):
    """
    Verify that the base template includes the viewport meta tag required for
    correct rendering on mobile, tablet, and desktop viewports.

    Requirement 6.2 — The Website SHALL render all pages correctly on mobile
    (320px–767px), tablet (768px–1023px), and desktop (1024px+) viewports.

    The ``<meta name="viewport" content="width=device-width, initial-scale=1.0">``
    tag is the fundamental browser signal that enables responsive layout;
    without it Bootstrap 5's breakpoints have no effect on real mobile devices.
    """

    VIEWPORT_META = 'content="width=device-width, initial-scale=1.0"'

    def _assert_has_viewport_meta(self, url: str):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200,
                         msg=f'Expected HTTP 200 for {url}')
        self.assertContains(
            response,
            self.VIEWPORT_META,
            msg_prefix=(
                f'Viewport meta tag missing from {url}. '
                f'Bootstrap 5 responsive breakpoints require '
                f'<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            ),
        )

    def test_home_page_has_viewport_meta(self):
        """Home page base template includes the viewport meta tag."""
        self._assert_has_viewport_meta('/')

    def test_gallery_page_has_viewport_meta(self):
        """Gallery page base template includes the viewport meta tag."""
        self._assert_has_viewport_meta('/gallery/')

    def test_apology_page_has_viewport_meta(self):
        """Apology page base template includes the viewport meta tag."""
        self._assert_has_viewport_meta('/apology/')


# ---------------------------------------------------------------------------
# Accessibility tests — skip navigation link and main landmark (Req 6.4, 6.5)
# ---------------------------------------------------------------------------


class SkipNavigationLinkTests(TestCase):
    """
    Verify that the base template includes a skip-to-content link and that
    the main landmark has the matching id, so keyboard and screen-reader
    users can bypass the navigation on every page.

    Requirement 6.4 — THE Website SHALL achieve a Lighthouse accessibility
    score of 80 or above.
    Requirement 6.5 — WHEN the Visitor uses keyboard navigation, THE Website
    SHALL provide visible focus indicators on all interactive elements.
    """

    SKIP_LINK_HREF = 'href="#main-content"'
    MAIN_ID = 'id="main-content"'

    def _assert_skip_link_present(self, url: str):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=f'Expected HTTP 200 for {url}')
        self.assertContains(
            response,
            self.SKIP_LINK_HREF,
            msg_prefix=f'Skip-to-content link (href="#main-content") missing from {url}',
        )
        self.assertContains(
            response,
            self.MAIN_ID,
            msg_prefix=f'<main id="main-content"> landmark missing from {url}',
        )

    def test_home_has_skip_link(self):
        """Home page renders both the skip link and the main landmark id."""
        self._assert_skip_link_present('/')

    def test_gallery_has_skip_link(self):
        """Gallery page renders both the skip link and the main landmark id."""
        self._assert_skip_link_present('/gallery/')

    def test_apology_has_skip_link(self):
        """Apology page renders both the skip link and the main landmark id."""
        self._assert_skip_link_present('/apology/')

    def test_skip_link_text_is_descriptive(self):
        """The skip link contains descriptive visible text for screen readers."""
        response = self.client.get('/')
        self.assertContains(
            response,
            'Skip to main content',
            msg_prefix='Skip link must have descriptive text "Skip to main content"',
        )


# ---------------------------------------------------------------------------
# Task 9.1 — WhiteNoise middleware configuration (Requirement 7.1)
# ---------------------------------------------------------------------------

from django.conf import settings as django_settings


class WhiteNoiseMiddlewareTests(TestCase):
    """
    Verify WhiteNoise middleware is configured correctly so that static assets
    are served with long-lived cache headers (Requirement 7.1).
    """

    def test_whitenoise_middleware_present(self):
        """WhiteNoiseMiddleware must be listed in MIDDLEWARE."""
        self.assertIn(
            'whitenoise.middleware.WhiteNoiseMiddleware',
            django_settings.MIDDLEWARE,
            msg='whitenoise.middleware.WhiteNoiseMiddleware must be in MIDDLEWARE',
        )

    def test_whitenoise_middleware_after_security_middleware(self):
        """WhiteNoiseMiddleware must appear immediately after SecurityMiddleware."""
        mw = django_settings.MIDDLEWARE
        security_idx = mw.index('django.middleware.security.SecurityMiddleware')
        whitenoise_idx = mw.index('whitenoise.middleware.WhiteNoiseMiddleware')
        self.assertGreater(
            whitenoise_idx,
            security_idx,
            msg='WhiteNoiseMiddleware must come after SecurityMiddleware in MIDDLEWARE',
        )


# ---------------------------------------------------------------------------
# Task 9.2 — compress_image smoke test (Requirements 7.3, 7.4)
# ---------------------------------------------------------------------------

import os
import tempfile


class CompressImageSmokeTests(TestCase):
    """
    Smoke test: compress_image reduces a real oversized JPEG to <= 2 MB.
    Requirements 7.3, 7.4
    """

    def test_compress_image_reduces_oversized_jpeg(self):
        """
        A JPEG larger than 2 MB must be reduced to <= 2 MB by compress_image.
        """
        from PIL import Image
        from memories.utils import compress_image

        TWO_MB = 2 * 1024 * 1024

        # Build a large image (3000×3000 RGB noise) and save as high-quality
        # JPEG to ensure it exceeds 2 MB on disk before compression.
        import random
        import struct

        width, height = 3000, 3000
        # Use a solid color with slight variation per row to defeat JPEG compression
        pixels = []
        for y in range(height):
            r = (y * 37) % 256
            g = (y * 53) % 256
            b = (y * 71) % 256
            pixels.extend([(r + (x % 16), g + (x % 16), b + (x % 16)) for x in range(width)])

        img = Image.new('RGB', (width, height))
        img.putdata(pixels)

        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        tmp.close()

        try:
            # Save at quality=95 to ensure the file is large
            img.save(tmp_path, format='JPEG', quality=95)
            initial_size = os.path.getsize(tmp_path)

            # Verify our test image is actually oversized (otherwise test is vacuous)
            self.assertGreater(
                initial_size,
                TWO_MB,
                msg=(
                    f'Test setup failed: generated image is only {initial_size} bytes; '
                    f'need > {TWO_MB} bytes to exercise compress_image.'
                ),
            )

            compress_image(tmp_path)

            final_size = os.path.getsize(tmp_path)
            self.assertLessEqual(
                final_size,
                TWO_MB,
                msg=(
                    f'compress_image did not reduce the file to <= 2 MB; '
                    f'final size: {final_size} bytes.'
                ),
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# ===========================================================================
# Task 10.1 — Unit tests for compress_image
# ===========================================================================


class CompressImageUnitTests(TestCase):
    """Unit tests for compress_image (Requirements 7.3, 7.4)."""

    TWO_MB = 2 * 1024 * 1024

    def _make_jpeg(self, width: int, height: int, quality: int = 85) -> str:
        """Save a solid-color JPEG to a temp file and return the path."""
        from PIL import Image
        img = Image.new('RGB', (width, height), color=(120, 80, 60))
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        tmp.close()
        img.save(tmp_path, format='JPEG', quality=quality)
        return tmp_path

    def test_below_2mb_file_unchanged(self):
        """A tiny JPEG (< 2 MB) must not be modified by compress_image."""
        from memories.utils import compress_image
        tmp_path = self._make_jpeg(10, 10)
        try:
            original_size = os.path.getsize(tmp_path)
            self.assertLess(original_size, self.TWO_MB,
                            'Test setup: image should be below 2 MB')
            compress_image(tmp_path)
            self.assertEqual(os.path.getsize(tmp_path), original_size,
                             'File size must not change for images below 2 MB')
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_at_2mb_file_unchanged(self):
        """A file at exactly 2 MB must not be modified by compress_image."""
        from memories.utils import compress_image

        # Create a raw binary file padded to exactly 2 MB.
        # compress_image checks getsize <= MAX_FILE_SIZE_BYTES before doing anything,
        # so a file of exactly 2 MB (== MAX_FILE_SIZE_BYTES) is left untouched.
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        tmp.write(b'\x00' * self.TWO_MB)
        tmp.close()
        try:
            self.assertEqual(os.path.getsize(tmp_path), self.TWO_MB,
                             'Test setup: file must be exactly 2 MB')
            compress_image(tmp_path)
            self.assertEqual(os.path.getsize(tmp_path), self.TWO_MB,
                             'File size must not change for a file at exactly 2 MB')
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_above_2mb_file_is_reduced(self):
        """A JPEG above 2 MB must be compressed to <= 2 MB by compress_image."""
        from PIL import Image
        from memories.utils import compress_image

        width, height = 3000, 3000
        pixels = []
        for y in range(height):
            r = (y * 37) % 256
            g = (y * 53) % 256
            b = (y * 71) % 256
            pixels.extend([(r + (x % 16), g + (x % 16), b + (x % 16)) for x in range(width)])
        img = Image.new('RGB', (width, height))
        img.putdata(pixels)
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        tmp.close()
        try:
            img.save(tmp_path, format='JPEG', quality=95)
            initial_size = os.path.getsize(tmp_path)
            self.assertGreater(initial_size, self.TWO_MB,
                               'Test setup: image must be > 2 MB before compression')
            compress_image(tmp_path)
            self.assertLessEqual(os.path.getsize(tmp_path), self.TWO_MB,
                                 'compress_image must reduce the file to <= 2 MB')
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_nonexistent_path_does_not_raise(self):
        """Calling compress_image on a non-existent path must not raise an exception."""
        from memories.utils import compress_image
        # Should silently return without raising
        compress_image('nonexistent_does_not_exist_12345.jpg')


# ===========================================================================
# Task 10.2 — Unit tests for _resize_to_fit
# ===========================================================================

from memories.utils import _resize_to_fit
from PIL import Image as PILImage


class ResizeToFitTests(TestCase):
    """Unit tests for _resize_to_fit dimension calculations."""

    def _make_img(self, width: int, height: int) -> PILImage.Image:
        return PILImage.new('RGB', (width, height), color=(200, 150, 100))

    def test_small_image_returned_unchanged(self):
        """100×100 image with max_dim=1920 must be returned at the same size."""
        img = self._make_img(100, 100)
        result = _resize_to_fit(img, 1920)
        self.assertEqual(result.size, (100, 100))

    def test_wide_image_scaled_correctly(self):
        """3840×1080 with max_dim=1920 → width=1920, height preserves aspect ratio."""
        img = self._make_img(3840, 1080)
        result = _resize_to_fit(img, 1920)
        self.assertEqual(result.width, 1920)
        # height should be int(1080 * (1920/3840)) = int(1080 * 0.5) = 540
        expected_height = int(1080 * (1920 / 3840))
        self.assertEqual(result.height, expected_height)

    def test_tall_image_scaled_correctly(self):
        """1080×3840 with max_dim=1920 → height=1920, width preserves aspect ratio."""
        img = self._make_img(1080, 3840)
        result = _resize_to_fit(img, 1920)
        self.assertEqual(result.height, 1920)
        # width should be int(1080 * (1920/3840))
        expected_width = int(1080 * (1920 / 3840))
        self.assertEqual(result.width, expected_width)

    def test_square_image_at_max_dim_unchanged(self):
        """1920×1920 must be returned unchanged (exactly at max_dim)."""
        img = self._make_img(1920, 1920)
        result = _resize_to_fit(img, 1920)
        self.assertEqual(result.size, (1920, 1920))

    def test_square_image_above_max_dim_scaled(self):
        """2000×2000 must be scaled to 1920×1920."""
        img = self._make_img(2000, 2000)
        result = _resize_to_fit(img, 1920)
        self.assertEqual(result.size, (1920, 1920))


# ===========================================================================
# Task 10.4 — Unit tests for SiteSettings.get() singleton
# ===========================================================================

from memories.models import SiteSettings


class SiteSettingsGetTests(TestCase):
    """Unit tests for SiteSettings.get() singleton behavior."""

    def test_get_creates_singleton_on_first_call(self):
        """get() must create exactly one SiteSettings row when none exist."""
        SiteSettings.objects.all().delete()
        self.assertEqual(SiteSettings.objects.count(), 0)
        SiteSettings.get()
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_get_returns_same_object_on_second_call(self):
        """Two consecutive get() calls must return objects with the same pk."""
        SiteSettings.objects.all().delete()
        obj1 = SiteSettings.get()
        obj2 = SiteSettings.get()
        self.assertEqual(obj1.pk, obj2.pk)

    def test_singleton_pk_is_always_1(self):
        """SiteSettings.get() must always return an object with pk=1."""
        SiteSettings.objects.all().delete()
        obj = SiteSettings.get()
        self.assertEqual(obj.pk, 1)

    def test_defaults_are_set(self):
        """welcome_message and apology_message must be non-None after get()."""
        SiteSettings.objects.all().delete()
        obj = SiteSettings.get()
        self.assertIsNotNone(obj.welcome_message)
        self.assertIsNotNone(obj.apology_message)

    def test_multiple_saves_enforce_singleton(self):
        """Multiple save() calls must never create more than one row."""
        SiteSettings.objects.all().delete()
        for i in range(5):
            obj = SiteSettings.get()
            obj.welcome_message = f'Update {i}'
            obj.save()
        self.assertEqual(SiteSettings.objects.count(), 1,
                         'Multiple save() calls must not create additional rows')

    def test_saved_values_retrievable_via_get(self):
        """Values saved to SiteSettings are returned by a subsequent get()."""
        SiteSettings.objects.all().delete()
        obj = SiteSettings.get()
        obj.welcome_message = 'Hello, Ana!'
        obj.apology_message = '<p>I am sorry.</p>'
        obj.save()

        retrieved = SiteSettings.get()
        self.assertEqual(retrieved.welcome_message, 'Hello, Ana!')
        self.assertEqual(retrieved.apology_message, '<p>I am sorry.</p>')


# ===========================================================================
# Tasks 10.5–10.11 — Property-based tests (Hypothesis)
# ===========================================================================

from hypothesis import given, settings as h_settings
from hypothesis import strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase


# ---------------------------------------------------------------------------
# Task 10.5 — Property 1: Image compression size bound
# ---------------------------------------------------------------------------

class Property1CompressionSizeBoundTests(HypothesisTestCase):
    # Feature: girlfriend-memory-website, Property 1: image compression size bound

    @given(
        width=st.integers(min_value=2000, max_value=4000),
        height=st.integers(min_value=2000, max_value=4000),
    )
    @h_settings(max_examples=20, deadline=None)
    def test_compress_image_size_bound(self, width, height):
        # Feature: girlfriend-memory-website, Property 1: image compression size bound
        from PIL import Image
        from memories.utils import compress_image

        TWO_MB = 2 * 1024 * 1024

        # Create a noisy image to defeat JPEG compression
        pixels = []
        for y in range(height):
            r = (y * 37) % 256
            g = (y * 53) % 256
            b = (y * 71) % 256
            pixels.extend([(r + (x % 16), g + (x % 16), b + (x % 16)) for x in range(width)])

        img = Image.new('RGB', (width, height))
        img.putdata(pixels)

        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        tmp.close()

        try:
            img.save(tmp_path, format='JPEG', quality=95)
            if os.path.getsize(tmp_path) > TWO_MB:
                compress_image(tmp_path)
                self.assertLessEqual(
                    os.path.getsize(tmp_path),
                    TWO_MB,
                    f'compress_image did not reduce {width}×{height} image to <= 2 MB',
                )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Task 10.6 — Property 2: Compression preserves image validity
# ---------------------------------------------------------------------------

class Property2CompressionValidityTests(HypothesisTestCase):
    # Feature: girlfriend-memory-website, Property 2: compression preserves image validity

    @given(
        width=st.integers(min_value=2000, max_value=4000),
        height=st.integers(min_value=2000, max_value=4000),
    )
    @h_settings(max_examples=20, deadline=None)
    def test_compress_image_preserves_validity(self, width, height):
        # Feature: girlfriend-memory-website, Property 2: compression preserves image validity
        # Validates: Requirements 7.3, 7.4
        #
        # For any uploaded JPEG image, after compress_image runs, the resulting file SHALL
        # still be openable as a valid image by Pillow without raising an exception.
        # This also verifies that files below 2 MB (not compressed) remain valid.
        from PIL import Image
        from memories.utils import compress_image

        TWO_MB = 2 * 1024 * 1024

        # Build a noisy image to defeat JPEG compression and ensure large file size
        pixels = []
        for y in range(height):
            r = (y * 37) % 256
            g = (y * 53) % 256
            b = (y * 71) % 256
            pixels.extend([(r + (x % 16), g + (x % 16), b + (x % 16)) for x in range(width)])

        img = Image.new('RGB', (width, height))
        img.putdata(pixels)

        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        tmp.close()

        try:
            # Save at quality=95 to ensure file is large (likely above 2 MB for large dims)
            img.save(tmp_path, format='JPEG', quality=95)

            # Call compress_image unconditionally — it handles the size check internally.
            # This also verifies files below 2 MB are not corrupted by compress_image.
            compress_image(tmp_path)

            # The file must still be openable as a valid image
            try:
                reopened = Image.open(tmp_path)
                # Accessing .size confirms the image can be decoded (header + metadata)
                _ = reopened.size
                reopened.close()
            except Exception as e:
                self.fail(
                    f'compress_image produced an invalid JPEG for {width}×{height}: {e}'
                )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @given(
        width=st.integers(min_value=2000, max_value=4000),
        height=st.integers(min_value=2000, max_value=4000),
    )
    @h_settings(max_examples=20, deadline=None)
    def test_compress_image_preserves_validity_for_large_files(self, width, height):
        # Feature: girlfriend-memory-website, Property 2: compression preserves image validity
        # Validates: Requirements 7.3, 7.4
        #
        # For images that are guaranteed to be above 2 MB (noisy pixels at quality=95),
        # compress_image SHALL produce a file that is still openable as a valid image.
        import random
        from PIL import Image
        from memories.utils import compress_image

        TWO_MB = 2 * 1024 * 1024

        # Use random noise pixels to maximally defeat JPEG compression
        rng = random.Random(width * 10000 + height)
        pixels = [
            (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            for _ in range(width * height)
        ]

        img = Image.new('RGB', (width, height))
        img.putdata(pixels)

        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        tmp.close()

        try:
            img.save(tmp_path, format='JPEG', quality=95)
            initial_size = os.path.getsize(tmp_path)

            # Only assert the validity property when the image is actually above 2 MB
            # (the noisy pixels at quality=95 should ensure this for 2000×2000+)
            if initial_size > TWO_MB:
                compress_image(tmp_path)

                try:
                    reopened = Image.open(tmp_path)
                    _ = reopened.size
                    reopened.close()
                except Exception as e:
                    self.fail(
                        f'compress_image produced an invalid JPEG for '
                        f'{width}×{height} (initial size={initial_size}): {e}'
                    )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Task 10.7 — Property 3: Caption length enforcement
# ---------------------------------------------------------------------------

from django.core.exceptions import ValidationError as DjangoValidationError


class Property3CaptionLengthTests(HypothesisTestCase):
    # Feature: girlfriend-memory-website, Property 3: caption length enforcement

    @given(caption=st.text(min_size=1, max_size=300))
    @h_settings(max_examples=100)
    def test_caption_up_to_300_chars_accepted(self, caption):
        # Feature: girlfriend-memory-website, Property 3: caption length enforcement
        # Validates: Requirements 2.1
        #
        # For any non-empty caption string of 300 characters or fewer, the Memory model
        # SHALL accept the value (full_clean must not raise ValidationError).
        # Note: min_size=1 because the caption field requires a non-blank value (blank=False).
        obj = Memory(caption=caption, display_order=0)
        try:
            obj.full_clean(exclude=['photo'])
        except DjangoValidationError as exc:
            # Only fail if the caption field itself raised the error
            if 'caption' in exc.message_dict:
                self.fail(
                    f'Caption of length {len(caption)} should be accepted but '
                    f'full_clean raised ValidationError for caption: {exc.message_dict["caption"]}'
                )

    @given(caption=st.text(min_size=301))
    @h_settings(max_examples=100)
    def test_caption_over_300_chars_rejected(self, caption):
        # Feature: girlfriend-memory-website, Property 3: caption length enforcement
        # Validates: Requirements 2.1
        #
        # For any caption string whose length exceeds 300 characters, validation
        # SHALL reject it (full_clean must raise ValidationError).
        obj = Memory(caption=caption, display_order=0)
        with self.assertRaises(DjangoValidationError):
            obj.full_clean(exclude=['photo'])


# ---------------------------------------------------------------------------
# Task 10.8 — Property 4: File extension validation
# ---------------------------------------------------------------------------

class Property4ExtensionValidationTests(HypothesisTestCase):
    # Feature: girlfriend-memory-website, Property 4: file extension validation

    @given(ext=st.sampled_from(['.jpg', '.jpeg', '.png', '.gif', '.webp']))
    @h_settings(max_examples=100)
    def test_valid_extension_does_not_raise(self, ext):
        # Feature: girlfriend-memory-website, Property 4: file extension validation
        # Validates: Requirements 5.6
        #
        # For any filename whose extension is in {.jpg, .jpeg, .png, .gif, .webp},
        # validate_image_extension SHALL not raise.
        from memories.utils import validate_image_extension
        mock_file = MagicMock()
        mock_file.name = f'testfile{ext}'
        try:
            validate_image_extension(mock_file)
        except DjangoValidationError:
            self.fail(
                f'validate_image_extension raised ValidationError for allowed extension: {ext}'
            )

    @given(ext=st.sampled_from(['.bmp', '.tiff', '.pdf', '.exe', '.svg', '.heic', '.txt', '.doc', '.mp4', '.zip']))
    @h_settings(max_examples=100)
    def test_invalid_extension_raises_with_descriptive_message(self, ext):
        # Feature: girlfriend-memory-website, Property 4: file extension validation
        # Validates: Requirements 5.6
        #
        # For any filename whose extension is NOT in {.jpg, .jpeg, .png, .gif, .webp},
        # validate_image_extension SHALL raise a ValidationError with a descriptive message.
        from memories.utils import validate_image_extension
        mock_file = MagicMock()
        mock_file.name = f'testfile{ext}'
        with self.assertRaises(DjangoValidationError) as ctx:
            validate_image_extension(mock_file)
        msg = str(ctx.exception)
        # The error message must be descriptive — mentioning allowed formats
        self.assertIn('JPEG', msg)
        self.assertIn('PNG', msg)
        self.assertIn('GIF', msg)
        self.assertIn('WebP', msg)


# ---------------------------------------------------------------------------
# Task 10.9 — Property 5: SiteSettings singleton and content round-trip
# ---------------------------------------------------------------------------

from hypothesis import HealthCheck

class Property5SiteSettingsSingletonTests(HypothesisTestCase):
    # Feature: girlfriend-memory-website, Property 5: SiteSettings singleton and content round-trip

    @given(
        pairs=st.lists(
            st.tuples(st.text(max_size=500), st.text(max_size=500)),
            min_size=1,
            max_size=10,
        )
    )
    @h_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_singleton_row_count_and_round_trip(self, pairs):
        # Feature: girlfriend-memory-website, Property 5: SiteSettings singleton and content round-trip
        # Validates: Requirements 3.6, 4.5, 5.3, 5.4
        #
        # For any sequence of (welcome_msg, apology_msg) pairs saved to SiteSettings,
        # there SHALL always be exactly one row in the SiteSettings table, and
        # SiteSettings.get() SHALL return the most-recently-saved values.
        from memories.models import SiteSettings

        # Ensure a clean slate for each example
        SiteSettings.objects.all().delete()

        for welcome_msg, apology_msg in pairs:
            obj = SiteSettings.get()
            obj.welcome_message = welcome_msg
            obj.apology_message = apology_msg
            obj.save()
            # Singleton invariant must hold after every save
            self.assertEqual(
                SiteSettings.objects.count(),
                1,
                f'Expected exactly 1 SiteSettings row after save, '
                f'got {SiteSettings.objects.count()}',
            )

        # After all saves, the retrieved object must match the last saved values
        last_welcome, last_apology = pairs[-1]
        retrieved = SiteSettings.get()
        self.assertEqual(
            retrieved.welcome_message,
            last_welcome,
            f'welcome_message mismatch: expected {last_welcome!r}, '
            f'got {retrieved.welcome_message!r}',
        )
        self.assertEqual(
            retrieved.apology_message,
            last_apology,
            f'apology_message mismatch: expected {last_apology!r}, '
            f'got {retrieved.apology_message!r}',
        )


# ---------------------------------------------------------------------------
# Task 10.10 — Property 6: Memory display order preserved on retrieval
# ---------------------------------------------------------------------------

from memories.models import Memory as MemoryModel


class Property6DisplayOrderTests(HypothesisTestCase):
    # Feature: girlfriend-memory-website, Property 6: Memory display order preserved on retrieval

    @given(
        orders=st.lists(
            st.integers(min_value=0, max_value=1000),
            min_size=1,
            max_size=10,
            unique=True,
        )
    )
    @h_settings(max_examples=100, deadline=None)
    def test_memories_retrieved_in_display_order(self, orders):
        # Feature: girlfriend-memory-website, Property 6: Memory display order preserved on retrieval
        # Validates: Requirements 5.2
        #
        # For any collection of Memory objects assigned distinct display_order values,
        # Memory.objects.all() SHALL return them sorted ascending by display_order.
        # Clean up any existing memories from previous examples
        MemoryModel.objects.all().delete()

        shuffled = list(orders)
        random.shuffle(shuffled)

        for order_val in shuffled:
            m = MemoryModel(caption=f'Memory {order_val}', display_order=order_val)
            m.save_base()

        retrieved_orders = list(
            MemoryModel.objects.all().values_list('display_order', flat=True)
        )
        self.assertEqual(
            retrieved_orders,
            sorted(orders),
            f'Expected order {sorted(orders)}, got {retrieved_orders}',
        )


# ---------------------------------------------------------------------------
# Task 10.11 — Property 7: Rendered memory contains required fields
# ---------------------------------------------------------------------------

import datetime


class Property7RenderedMemoryFieldsTests(HypothesisTestCase):
    # Feature: girlfriend-memory-website, Property 7: rendered memory contains required fields

    @given(
        caption=st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs')),
        ),
        has_date=st.booleans(),
    )
    @h_settings(max_examples=100, deadline=None)
    def test_rendered_gallery_contains_required_fields(self, caption, has_date):
        # Feature: girlfriend-memory-website, Property 7: rendered memory contains required fields
        # Validates: Requirements 2.3, 6.3
        #
        # For any Memory object with a caption and optional date, the rendered gallery
        # template HTML SHALL contain the caption text, the date (if present), and a
        # non-empty alt attribute on the <img> element.
        MemoryModel.objects.all().delete()

        memory = MemoryModel(
            caption=caption,
            display_order=1,
        )
        if has_date:
            memory.date = datetime.date(2024, 6, 15)
        # Assign a dummy photo path so the template can render photo.url
        memory.save_base()
        memory.photo.name = 'memories/dummy_prop7.jpg'
        memory.save_base(update_fields=['photo'])

        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Caption must appear in the rendered HTML
        self.assertIn(caption, content,
                      f'Caption "{caption}" not found in gallery HTML')

        # If date is set, a datetime attribute must appear (from the <time> element)
        if has_date:
            self.assertIn('datetime=', content,
                          'datetime attribute not found in gallery HTML when date is set')

        # An alt attribute must be present (from the <img> element)
        self.assertIn('alt=', content,
                      'alt attribute not found in gallery HTML')
        # The alt attribute must not be empty when there is a caption
        self.assertNotIn('alt=""', content,
                         'Empty alt attribute found in gallery HTML')


# ===========================================================================
# Task 10.12 — Admin upload integration: invalid file test
# ===========================================================================

class AdminInvalidUploadTests(TestCase):
    """Integration test: uploading a non-image file via admin must show a form error."""

    @classmethod
    def setUpTestData(cls):
        User = __import__('django.contrib.auth', fromlist=['get_user_model']).get_user_model()
        cls.superuser = User.objects.create_superuser(
            username='admin_invalid_test',
            password='testpassword123',
            email='admin_invalid@test.com',
        )

    def setUp(self):
        self.client.force_login(self.superuser)

    @override_settings(MEDIA_ROOT='/tmp/test_media_memories')
    def test_upload_invalid_file_shows_form_error(self):
        """POST a .txt file to admin add URL → 200 (form re-shown), no Memory created."""
        from django.urls import reverse
        add_url = reverse('admin:memories_memory_add')

        txt_file = io.BytesIO(b'This is not an image file.')
        txt_file.name = 'document.txt'

        initial_count = MemoryModel.objects.count()
        response = self.client.post(
            add_url,
            data={
                'photo': txt_file,
                'caption': 'Should be rejected',
                'display_order': '99',
                '_save': 'Save',
            },
        )
        # Admin re-shows the form with errors (HTTP 200) rather than redirecting
        self.assertEqual(response.status_code, 200,
                         'Expected HTTP 200 (form re-shown with error) for invalid file upload')
        self.assertEqual(MemoryModel.objects.count(), initial_count,
                         'No Memory should be created when an invalid file is uploaded')


# ===========================================================================
# Task 10.13 — Gallery, apology, home view integration tests
# ===========================================================================

class ViewIntegrationTests(TestCase):
    """Integration tests for gallery, home, and apology views."""

    def test_home_returns_200(self):
        """GET / → HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_context_has_welcome_message(self):
        """Home view context must include welcome_message."""
        response = self.client.get('/')
        self.assertIn('welcome_message', response.context)

    def test_home_context_has_memories(self):
        """Home view context must include memories."""
        response = self.client.get('/')
        self.assertIn('memories', response.context)

    def test_gallery_returns_200(self):
        """GET /gallery/ → HTTP 200."""
        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)

    def test_gallery_context_has_pages(self):
        """Gallery view context must include pages."""
        response = self.client.get('/gallery/')
        self.assertIn('pages', response.context)

    def test_gallery_context_has_memories_json(self):
        """Gallery view context must include memories_json."""
        response = self.client.get('/gallery/')
        self.assertIn('memories_json', response.context)

    def test_apology_returns_200(self):
        """GET /apology/ → HTTP 200."""
        response = self.client.get('/apology/')
        self.assertEqual(response.status_code, 200)

    def test_hero_section_present_on_home(self):
        """Home page must include the hero-section class."""
        response = self.client.get('/')
        self.assertContains(response, 'hero-section')

    def test_nav_links_present_on_all_pages(self):
        """Gallery and Apology nav links must appear on the home page."""
        response = self.client.get('/')
        self.assertContains(response, 'href="/gallery/"',
                            msg_prefix='Gallery nav link not found on home page')
        self.assertContains(response, 'href="/apology/"',
                            msg_prefix='Apology nav link not found on home page')

    def test_gallery_renders_img_tags_for_memories(self):
        """Gallery page must render <img> tags when memories with photos exist."""
        # Create a memory with a dummy photo path so gallery template renders <img>
        memory = Memory.objects.create(caption='Gallery photo', display_order=1)
        memory.photo.name = 'memories/dummy_gallery_img.jpg'
        memory.save_base(update_fields=['photo'])

        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<img',
                            msg_prefix='Expected <img> tag in gallery page when memories exist')

    def test_apology_context_has_apology_message(self):
        """Apology view context must include apology_message."""
        response = self.client.get('/apology/')
        self.assertIn('apology_message', response.context)

    def test_sitesettings_update_reflected_on_home_page(self):
        """
        Updating SiteSettings.welcome_message must be reflected on the home page.
        Integration test: update model directly, verify GET / returns the new message.
        """
        unique_message = 'UNIQUE_WELCOME_MSG_XYZ_12345'
        site_settings = SiteSettings.get()
        site_settings.welcome_message = unique_message
        site_settings.save()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            unique_message,
            msg_prefix='Updated welcome_message must appear on the home page',
        )


# ---------------------------------------------------------------------------
# Task 11.3 — Static file serving with DEBUG=False (Requirement 8.3)
# ---------------------------------------------------------------------------


class StaticFilesDebugFalseTests(TestCase):
    """
    Verify that the configuration correctly supports serving static files from
    STATIC_ROOT when DEBUG=False, as required by Requirement 8.3.

    WhiteNoise middleware handles static file serving both with DEBUG=True and
    DEBUG=False, eliminating the need for a separate static file server in
    production.
    """

    def test_static_root_is_configured(self):
        """STATIC_ROOT must be set to a non-None, non-empty value."""
        self.assertIsNotNone(
            django_settings.STATIC_ROOT,
            msg='STATIC_ROOT must be configured for static file serving with DEBUG=False',
        )
        self.assertTrue(
            str(django_settings.STATIC_ROOT),
            msg='STATIC_ROOT must not be empty',
        )

    def test_whitenoise_storage_backend_configured(self):
        """
        The staticfiles storage backend must be WhiteNoise's
        CompressedManifestStaticFilesStorage, which serves files with hashed
        filenames and pre-compressed .gz copies for efficient production serving.
        """
        staticfiles_backend = django_settings.STORAGES['staticfiles']['BACKEND']
        self.assertEqual(
            staticfiles_backend,
            'whitenoise.storage.CompressedManifestStaticFilesStorage',
            msg=(
                'STORAGES["staticfiles"]["BACKEND"] must be '
                '"whitenoise.storage.CompressedManifestStaticFilesStorage" '
                'for efficient static file serving when DEBUG=False'
            ),
        )

    def test_whitenoise_middleware_present_for_debug_false(self):
        """
        WhiteNoiseMiddleware must be in MIDDLEWARE — this is what serves static
        files from STATIC_ROOT when DEBUG=False.
        Validates: Requirement 8.3
        """
        self.assertIn(
            'whitenoise.middleware.WhiteNoiseMiddleware',
            django_settings.MIDDLEWARE,
            msg=(
                'whitenoise.middleware.WhiteNoiseMiddleware must be in MIDDLEWARE '
                'to serve static files from STATIC_ROOT when DEBUG=False'
            ),
        )

    def test_static_root_exists(self):
        """
        The STATIC_ROOT directory must exist on disk (i.e. collectstatic has
        been run and populated it).
        """
        import os
        self.assertTrue(
            os.path.isdir(django_settings.STATIC_ROOT),
            msg=(
                f'STATIC_ROOT directory "{django_settings.STATIC_ROOT}" does not exist. '
                f'Run "python manage.py collectstatic --no-input" to populate it.'
            ),
        )


# ---------------------------------------------------------------------------
# Task 11.4 — DATABASE_URL switches to PostgreSQL when set (Requirement 8.5)
# ---------------------------------------------------------------------------


class DatabaseUrlConfigTests(TestCase):
    """
    Verify that the database configuration correctly uses SQLite by default
    and switches to PostgreSQL when DATABASE_URL is set to a postgres:// URL.

    Requirement 8.5 — The Website SHALL use SQLite as the default database for
    local development and support PostgreSQL as a production database via the
    DATABASE_URL environment variable.
    """

    def test_default_database_backend_is_sqlite(self):
        """
        When DATABASE_URL is not set (the default), the configured database
        backend must be django.db.backends.sqlite3.
        Validates: Requirement 8.5
        """
        self.assertEqual(
            django_settings.DATABASES['default']['ENGINE'],
            'django.db.backends.sqlite3',
            msg=(
                'The default database ENGINE must be "django.db.backends.sqlite3" '
                'when DATABASE_URL is not set.'
            ),
        )

    def test_postgres_url_parses_to_postgresql_engine(self):
        """
        dj_database_url.parse() on a postgres:// URL must return a config dict
        with ENGINE = 'django.db.backends.postgresql'.
        No actual database connection is made — this only tests the parse output.
        Validates: Requirement 8.5
        """
        import dj_database_url

        pg_url = 'postgres://user:password@localhost:5432/testdb'
        db_config = dj_database_url.parse(pg_url)

        self.assertEqual(
            db_config['ENGINE'],
            'django.db.backends.postgresql',
            msg=(
                f'dj_database_url.parse("{pg_url}") must return ENGINE = '
                '"django.db.backends.postgresql".'
            ),
        )

    def test_postgres_url_parses_correct_db_name(self):
        """
        dj_database_url.parse() on a postgres:// URL must return the correct
        database NAME from the URL path.
        Validates: Requirement 8.5
        """
        import dj_database_url

        pg_url = 'postgres://user:password@localhost:5432/testdb'
        db_config = dj_database_url.parse(pg_url)

        self.assertEqual(
            db_config['NAME'],
            'testdb',
            msg='dj_database_url.parse() must correctly extract the database name from the URL.',
        )
