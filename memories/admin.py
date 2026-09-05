from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import BvPhoto, GalleryMedia, HomeMedia, Memory, SiteSettings

admin.site.site_header = '♥ Memories Admin'
admin.site.site_title = 'Memories Admin'
admin.site.index_title = 'Welcome — Manage Your Content'


class FlexibleDateAdmin(admin.ModelAdmin):
    """Ensures dates entered as DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD are all accepted."""
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.DateField):
            kwargs['input_formats'] = [
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%y',
                '%d-%m-%y',
                '%Y/%m/%d',
            ]
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            if formfield and hasattr(formfield, 'widget'):
                formfield.widget.attrs.update({
                    'placeholder': 'DD/MM/YYYY (e.g. 16/6/2026)',
                })
            return formfield
        return super().formfield_for_dbfield(db_field, request, **kwargs)


def _render_thumb(obj):
    try:
        if getattr(obj, 'media_type', None) == 'video' and getattr(obj, 'video', None):
            return format_html(
                '<a href="{0}" target="_blank" title="Click to play video in new tab">'
                '<div style="width:52px;height:52px;border-radius:12px;background:#fef2f2;border:1px solid #fecaca;display:flex;align-items:center;justify-content:center;color:#ef4444;font-size:1.3rem;box-shadow:0 2px 8px rgba(0,0,0,0.05);">'
                '🎥'
                '</div>'
                '</a>',
                obj.video.url,
            )
        elif getattr(obj, 'photo', None):
            return format_html(
                '<a href="{0}" target="_blank" title="Click to view image in new tab">'
                '<img src="{0}" style="width:52px;height:52px;object-fit:cover;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);border:1px solid #e2e8f0;display:block;">'
                '</a>',
                obj.photo.url,
            )
    except Exception:
        pass
    return mark_safe('<span style="color:#94a3b8;font-size:0.85rem;">—</span>')


def _render_type_badge(obj):
    if getattr(obj, 'media_type', None) == 'video':
        return mark_safe(
            '<span style="background:#fef2f2;color:#dc2626;border:1px solid #fecaca;padding:3px 10px;border-radius:999px;font-size:0.78rem;font-weight:600;display:inline-flex;align-items:center;gap:4px;">🎥 Video</span>'
        )
    return mark_safe(
        '<span style="background:#ecfdf5;color:#059669;border:1px solid #a7f3d0;padding:3px 10px;border-radius:999px;font-size:0.78rem;font-weight:600;display:inline-flex;align-items:center;gap:4px;">📷 Photo</span>'
    )


def _render_row_actions(obj):
    app_label = obj._meta.app_label
    model_name = obj._meta.model_name
    change_url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.pk])
    delete_url = reverse(f'admin:{app_label}_{model_name}_delete', args=[obj.pk])
    return format_html(
        '<div class="row-actions-group">'
        '<a href="{}" class="btn-row-edit" title="Edit entry"><i class="fas fa-pen"></i></a>'
        '<a href="{}" class="btn-row-delete" title="Delete entry"><i class="fas fa-trash-alt"></i></a>'
        '</div>',
        change_url,
        delete_url,
    )


# ── Home Media ─────────────────────────────────────────────
@admin.register(HomeMedia)
class HomeMediaAdmin(admin.ModelAdmin):
    list_display = ('display_order', 'thumb', 'media_type_badge', 'caption', 'uploaded_at', 'row_actions')
    list_display_links = ('thumb', 'caption')
    list_editable = ('display_order',)
    list_filter = ('media_type',)
    ordering = ('display_order',)
    fieldsets = (
        ('Home Slide Details', {
            'fields': ('caption', 'display_order', 'alt_text'),
            'description': 'These photos/videos will be displayed on the Home Page hero slideshow.',
        }),
        ('Media File', {
            'fields': ('media_type', 'photo', 'video'),
            'description': 'Choose Photo or Video, then upload the file.',
        }),
    )

    def thumb(self, obj):
        return _render_thumb(obj)
    thumb.short_description = 'Preview'

    def media_type_badge(self, obj):
        return _render_type_badge(obj)
    media_type_badge.short_description = 'Type'

    def row_actions(self, obj):
        return _render_row_actions(obj)
    row_actions.short_description = 'Actions'


# ── Gallery Media ──────────────────────────────────────────
@admin.register(GalleryMedia)
class GalleryMediaAdmin(FlexibleDateAdmin):
    list_display = ('display_order', 'thumb', 'media_type_badge', 'caption', 'date', 'uploaded_at', 'row_actions')
    list_display_links = ('thumb', 'caption')
    list_editable = ('display_order',)
    list_filter = ('media_type', 'date')
    date_hierarchy = 'date'
    ordering = ('display_order',)
    fieldsets = (
        ('Gallery Item Details', {
            'fields': ('caption', 'date', 'display_order', 'alt_text'),
            'description': 'These photos/videos will be displayed in the Gallery (Book Flip, Carousel, Fade).',
        }),
        ('Media File', {
            'fields': ('media_type', 'photo', 'video'),
            'description': 'Choose Photo or Video, then upload the file.',
        }),
    )

    def thumb(self, obj):
        return _render_thumb(obj)
    thumb.short_description = 'Preview'

    def media_type_badge(self, obj):
        return _render_type_badge(obj)
    media_type_badge.short_description = 'Type'

    def row_actions(self, obj):
        return _render_row_actions(obj)
    row_actions.short_description = 'Actions'


# ── Timeline Memories ──────────────────────────────────────
@admin.register(Memory)
class MemoryAdmin(FlexibleDateAdmin):
    list_display = ('display_order', 'thumb', 'media_type_badge', 'caption', 'date', 'uploaded_at', 'row_actions')
    list_display_links = ('thumb', 'caption')
    list_editable = ('display_order',)
    list_filter = ('media_type',)
    ordering = ('display_order',)
    fieldsets = (
        ('Timeline Memory Details', {
            'fields': ('caption', 'date', 'display_order', 'alt_text'),
            'description': 'These memories appear in the interactive Story Timeline grouped by Year, Month, and Date.',
        }),
        ('Media File', {
            'fields': ('media_type', 'photo', 'video'),
            'description': 'Choose Photo or Video, then upload the file.',
        }),
    )

    def thumb(self, obj):
        return _render_thumb(obj)
    thumb.short_description = 'Preview'

    def media_type_badge(self, obj):
        return _render_type_badge(obj)
    media_type_badge.short_description = 'Type'

    def row_actions(self, obj):
        return _render_row_actions(obj)
    row_actions.short_description = 'Actions'


# ── BV Photos ──────────────────────────────────────────────
@admin.register(BvPhoto)
class BvPhotoAdmin(admin.ModelAdmin):
    list_display = ('display_order', 'thumb', 'caption', 'date', 'uploaded_at', 'row_actions')
    list_display_links = ('thumb', 'caption')
    list_editable = ('display_order',)
    ordering = ('display_order',)
    fields = ('photo', 'caption', 'date', 'display_order', 'alt_text')

    def thumb(self, obj):
        return _render_thumb(obj)
    thumb.short_description = 'Preview'

    def row_actions(self, obj):
        return _render_row_actions(obj)
    row_actions.short_description = 'Actions'


# ── Site Settings ──────────────────────────────────────────
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Home Welcome & Audio', {
            'fields': ('welcome_message', 'background_audio', 'apology_message'),
        }),
        ('Love Quote Banner Video', {
            'fields': ('quote_video', 'quote_text', 'quote_author'),
            'description': 'Upload a video to play as the background of the Love Quote Banner on the Home page.',
        }),
    )

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
