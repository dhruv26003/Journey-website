from .models import SiteSettings


def site_audio(request):
    """Make background_audio_url available in every template."""
    try:
        s = SiteSettings.get()
        url = s.background_audio.url if s.background_audio else ''
    except Exception:
        url = ''
    return {'background_audio_url': url}
