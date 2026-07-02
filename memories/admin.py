from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from .models import BvPhoto, Memory, SiteSettings

admin.site.site_header = '♥ Memories Admin'
admin.site.site_title = 'Memories Admin'
admin.site.index_title = 'Welcome — Manage Your Memories'


# ── BV Photos ──────────────────────────────────────────────
@admin.register(BvPhoto)
class BvPhotoAdmin(admin.ModelAdmin):
    list_display = ('display_order', 'thumb', 'caption', 'date', 'uploaded_at')
    list_display_links = ('caption',)
    list_editable = ('display_order',)
    ordering = ('display_order',)
    fields = ('photo', 'caption', 'date', 'display_order', 'alt_text')

    def thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:56px;height:56px;object-fit:cover;border-radius:6px;border:2px solid #e8c8bf;">',
                obj.photo.url,
            )
        return '—'
    thumb.short_description = 'Preview'


# ── Memories ───────────────────────────────────────────────
@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('display_order', 'media_type_badge', 'caption', 'date', 'uploaded_at')
    list_display_links = ('caption',)
    list_editable = ('display_order',)
    list_filter = ('media_type',)
    ordering = ('display_order',)
    fieldsets = (
        ('Memory Details', {'fields': ('caption', 'date', 'display_order', 'alt_text')}),
        ('Media', {
            'fields': ('media_type', 'photo', 'video'),
            'description': 'Choose Photo or Video, then upload the file.',
        }),
    )
    def media_type_badge(self, obj):
        if obj.media_type == Memory.MEDIA_TYPE_VIDEO:
            return format_html(
                '<span style="background:#c0605a;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8em;">{}</span>',
                "🎥 Video",
            )

        return format_html(
            '<span style="background:#6a9e6a;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8em;">{}</span>',
            "📷 Photo",
        )
    media_type_badge.short_description = "Type"


# ── Site Settings ──────────────────────────────────────────
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fields = ('welcome_message', 'apology_message', 'background_audio')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '',
                self.admin_site.admin_view(self._redirect),
                name='memories_sitesettings_changelist',
            ),
        ]
        return custom + [u for u in urls if u.name != 'memories_sitesettings_changelist']

    def _redirect(self, request):
        SiteSettings.get()
        return HttpResponseRedirect(
            reverse('admin:memories_sitesettings_change', args=[1], current_app=self.admin_site.name)
        )
