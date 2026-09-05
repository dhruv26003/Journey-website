import json
from collections import defaultdict

from django.views.generic import TemplateView

from .models import BvPhoto, GalleryMedia, HomeMedia, Memory, SiteSettings


MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']


def _memory_to_dict(m):
    date_val = m.date.isoformat() if getattr(m, 'date', None) else ''
    date_formatted = m.date.strftime('%B %d, %Y') if getattr(m, 'date', None) else ''
    year = m.date.year if getattr(m, 'date', None) else None
    month = m.date.month if getattr(m, 'date', None) else None
    month_name = MONTH_NAMES[month] if month else ''
    return {
        'id': m.id,
        'media_type': m.media_type,
        'is_video': m.is_video,
        'photo_url': m.photo.url if m.photo else '',
        'video_url': m.video.url if m.video else '',
        'media_url': m.media_url,
        'caption': m.caption,
        'date': date_val,
        'date_formatted': date_formatted,
        'year': year,
        'month': month,
        'month_name': month_name,
        'alt_text': m.alt_text or m.caption,
        'display_order': m.display_order,
    }


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        s = SiteSettings.get()
        ctx['welcome_message'] = s.welcome_message
        ctx['quote_text'] = s.quote_text or '"You are my today and all of my tomorrows."'
        ctx['quote_author'] = s.quote_author or 'Leo Christopher'

        # Banner video resolution: SiteSettings video, fallback to first video in HomeMedia/Memory
        if s.quote_video:
            ctx['banner_video_url'] = s.quote_video.url
        else:
            first_vid = HomeMedia.objects.filter(media_type='video').first() or Memory.objects.filter(media_type='video').first()
            ctx['banner_video_url'] = first_vid.video.url if (first_vid and first_vid.video) else ''
        ctx['home_video_url'] = ctx['banner_video_url']

        home_items = HomeMedia.objects.all()
        # Graceful fallback if no HomeMedia has been uploaded yet
        if not home_items.exists():
            home_items = Memory.objects.all()
        ctx['memories'] = home_items
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
        gallery_items = list(GalleryMedia.objects.all())
        # Graceful fallback if no GalleryMedia has been uploaded yet
        if not gallery_items:
            gallery_items = list(Memory.objects.all())

        # Group by Year and Month
        dated_items = [m for m in gallery_items if getattr(m, 'date', None)]
        undated_items = [m for m in gallery_items if not getattr(m, 'date', None)]

        tree = defaultdict(lambda: defaultdict(list))
        for m in dated_items:
            tree[m.date.year][m.date.month].append(m)

        years_data = []
        for year in sorted(tree.keys(), reverse=True):
            months_data = []
            for month_num in sorted(tree[year].keys(), reverse=True):
                m_items = sorted(tree[year][month_num], key=lambda x: (x.date, x.display_order))
                months_data.append({
                    'month_num': month_num,
                    'month_name': MONTH_NAMES[month_num],
                    'month_key': f"{year}-{month_num:02d}",
                    'count': len(m_items),
                    'items': m_items,
                })
            years_data.append({
                'year': year,
                'count': sum(m['count'] for m in months_data),
                'months': months_data,
            })

        ctx['years_data'] = years_data
        ctx['undated_items'] = undated_items
        ctx['total_gallery_count'] = len(gallery_items)
        ctx['pages'] = [gallery_items[i:i + 2] for i in range(0, len(gallery_items), 2)]
        ctx['memories_json'] = json.dumps([_memory_to_dict(m) for m in gallery_items])
        return ctx


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
