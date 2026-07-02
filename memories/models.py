import os

from django.db import models

from .utils import compress_image, validate_image_extension, validate_video_extension


class Memory(models.Model):
    MEDIA_TYPE_PHOTO = 'photo'
    MEDIA_TYPE_VIDEO = 'video'
    MEDIA_TYPE_CHOICES = [
        (MEDIA_TYPE_PHOTO, 'Photo'),
        (MEDIA_TYPE_VIDEO, 'Video'),
    ]

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default=MEDIA_TYPE_PHOTO,
        help_text='Choose whether this memory is a photo or a video.',
    )
    photo = models.ImageField(
        upload_to='memories/photos/',
        validators=[validate_image_extension],
        null=True,
        blank=True,
        help_text='Upload a photo (JPG, PNG, GIF, WebP).',
    )
    video = models.FileField(
        upload_to='memories/videos/',
        validators=[validate_video_extension],
        null=True,
        blank=True,
        help_text='Upload a video (MP4, WebM, MOV, M4V).',
    )
    caption = models.CharField(max_length=300)
    date = models.DateField(null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    alt_text = models.CharField(max_length=200, default='', blank=True, help_text='Screen reader description')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Memories'

    def __str__(self):
        date_str = self.date.isoformat() if self.date else 'undated'
        icon = 'Video' if self.media_type == self.MEDIA_TYPE_VIDEO else 'Photo'
        return f'[{icon}] Memory #{self.display_order} — {date_str}: {self.caption[:40]}'

    @property
    def is_video(self):
        return self.media_type == self.MEDIA_TYPE_VIDEO

    @property
    def media_url(self):
        if self.is_video and self.video:
            return self.video.url
        if self.photo:
            return self.photo.url
        return ''

    def save(self, *args, **kwargs):
        if self.media_type == self.MEDIA_TYPE_PHOTO and self.photo:
            try:
                from .utils import convert_and_compress_to_webp
                convert_and_compress_to_webp(self.photo)
            except Exception:
                pass
        super().save(*args, **kwargs)


class BvPhoto(models.Model):
    """BV (Best Friend) photos — completely separate from Memories."""
    photo = models.ImageField(
        upload_to='bv/photos/',
        validators=[validate_image_extension],
        help_text='Upload a photo (JPG, PNG, GIF, WebP).',
    )
    caption = models.CharField(max_length=300, blank=True, default='')
    date = models.DateField(null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    alt_text = models.CharField(max_length=200, default='', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'date']
        verbose_name = 'BV Photo'
        verbose_name_plural = 'BV Photos'

    def __str__(self):
        date_str = self.date.isoformat() if self.date else 'undated'
        return f'BV #{self.display_order} — {date_str}: {self.caption[:40]}'

    def save(self, *args, **kwargs):
        if self.photo:
            try:
                from .utils import convert_and_compress_to_webp
                convert_and_compress_to_webp(self.photo)
            except Exception:
                pass
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    welcome_message = models.TextField(
        default='Welcome to our memories.',
        help_text='Displayed on the home page hero section',
    )
    apology_message = models.TextField(
        default='',
        help_text='HTML-safe apology text. <p>, <em>, <br> supported.',
    )
    background_audio = models.FileField(
        upload_to='audio/',
        null=True,
        blank=True,
        help_text='Background music for the home page (MP3, OGG, WAV). Plays on user interaction.',
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
