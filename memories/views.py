import json
from collections import defaultdict

from django.views.generic import TemplateView

from .models import BvPhoto, Memory, SiteSettings


def _memory_to_dict(m):
    return {
        'id': m.id,
        'media_type': m.media_type,
        'is_video': m.is_video,
        'photo_url': m.photo.url if m.photo else '',
        'video_url': m.video.url if m.video else '',
        'media_url': m.media_url,
        'caption': m.caption,
        'date': m.date.isoformat() if m.date else '',
        'alt_text': m.alt_text or m.caption,
        'display_order': m.display_order,
    }


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        s = SiteSettings.get()
        ctx['welcome_message'] = s.welcome_message
        ctx['memories'] = Memory.objects.all()
        ctx['background_audio_url'] = s.background_audio.url if s.background_audio else ''
        return ctx


class ApologyView(TemplateView):
    template_name = 'apology.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['apology_message'] = SiteSettings.get().apology_message
        return ctx


class GalleryView(TemplateView):
    template_name = 'gallery.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        memories = list(Memory.objects.all())
        ctx['pages'] = [memories[i:i + 2] for i in range(0, len(memories), 2)]
        ctx['memories_json'] = json.dumps([_memory_to_dict(m) for m in memories])
        return ctx


MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']


class TimelineView(TemplateView):
    template_name = 'timeline.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        dated = Memory.objects.exclude(date=None).order_by('date', 'display_order')
        undated = Memory.objects.filter(date=None).order_by('display_order')

        tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for m in dated:
            tree[m.date.year][m.date.month][m.date.day].append(m)

        timeline = []
        for year in sorted(tree.keys(), reverse=True):
            months = []
            for month_num in sorted(tree[year].keys()):
                days = [(day, tree[year][month_num][day]) for day in sorted(tree[year][month_num].keys())]
                months.append((month_num, MONTH_NAMES[month_num], days))
            timeline.append((year, months))

        ctx['timeline'] = timeline
        ctx['undated'] = list(undated)
        ctx['total_count'] = dated.count() + undated.count()
        return ctx


class BvView(TemplateView):
    template_name = 'bv.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['photos'] = BvPhoto.objects.all()
        ctx['total'] = BvPhoto.objects.count()
        return ctx
