import io
import logging
import os

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB
MAX_DIMENSION = 1920  # px — long edge cap

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.m4v'}


def validate_video_extension(value):
    """Validate that the uploaded file is a supported video format."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            f'Unsupported video format "{ext}". '
            f'Allowed formats: MP4, WebM, MOV, M4V.'
        )


def compress_image(path: str) -> None:
    """Resize and re-save image in-place if it exceeds MAX_FILE_SIZE_BYTES."""
    if not os.path.exists(path):
        return
    if os.path.getsize(path) <= MAX_FILE_SIZE_BYTES:
        return
    try:
        with Image.open(path) as img:
            img = _resize_to_fit(img, MAX_DIMENSION)
            quality = 85
            while quality >= 40:
                img.save(path, optimize=True, quality=quality)
                if os.path.getsize(path) <= MAX_FILE_SIZE_BYTES:
                    break
                quality -= 10
            else:
                logger.warning(
                    'compress_image: could not reduce %s to <= %d bytes at minimum quality.',
                    path,
                    MAX_FILE_SIZE_BYTES,
                )
    except Exception as exc:
        logger.warning('compress_image: failed to process %s — %s', path, exc)


def _resize_to_fit(img: Image.Image, max_dim: int) -> Image.Image:
    """Return a resized copy of img so the long edge fits within max_dim."""
    w, h = img.size
    if max(w, h) <= max_dim:
        return img
    ratio = max_dim / max(w, h)
    return img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)


def validate_image_extension(value) -> None:
    """Django field validator: reject files whose extension is not in ALLOWED_EXTENSIONS."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'Unsupported file format "{ext}". '
            f'Allowed formats: JPEG, PNG, GIF, WebP.'
        )


def convert_and_compress_to_webp(image_field) -> None:
    """Resize and compress an image in-place, converting it to WebP format."""
    if not image_field:
        return

    try:
        # Save current position and read content
        image_field.seek(0)
        file_content = image_field.read()
        image_field.seek(0)

        if not file_content:
            return

        # Load into PIL
        with Image.open(io.BytesIO(file_content)) as img:
            orig_format = (img.format or "").upper()

            # Skip conversion for animated GIFs to preserve animation
            if orig_format == 'GIF':
                return

            # Skip if already WebP and size is within limits
            is_webp = image_field.name.lower().endswith('.webp')
            if is_webp and len(file_content) <= MAX_FILE_SIZE_BYTES:
                return

            # Resize if long edge > MAX_DIMENSION (1920)
            w, h = img.size
            if max(w, h) > MAX_DIMENSION:
                ratio = MAX_DIMENSION / max(w, h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

            # Convert to WebP and save to buffer
            buffer = io.BytesIO()
            
            # WebP supports RGBA (transparency), but we ensure mode compatibility
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img.save(buffer, format='WEBP', quality=80, method=4)
            else:
                img_conv = img.convert('RGB')
                img_conv.save(buffer, format='WEBP', quality=80, method=4)

            webp_data = buffer.getvalue()

            # Iterative compression if size still exceeds limit
            if len(webp_data) > MAX_FILE_SIZE_BYTES:
                quality = 70
                while quality >= 40:
                    buffer = io.BytesIO()
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        img.save(buffer, format='WEBP', quality=quality, method=4)
                    else:
                        img_conv = img.convert('RGB')
                        img_conv.save(buffer, format='WEBP', quality=quality, method=4)
                    webp_data = buffer.getvalue()
                    if len(webp_data) <= MAX_FILE_SIZE_BYTES:
                        break
                    quality -= 10

            # Generate WebP filename
            base_name = os.path.splitext(os.path.basename(image_field.name))[0]
            new_filename = f"{base_name}.webp"

            # Save file content back to the field
            image_field.save(new_filename, ContentFile(webp_data), save=False)

    except Exception as exc:
        logger.warning('convert_and_compress_to_webp: failed to process %s — %s', image_field.name, exc)

