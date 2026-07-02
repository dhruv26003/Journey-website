from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from memories.views import ApologyView, BvView, GalleryView, HomeView, TimelineView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("gallery/", GalleryView.as_view(), name="gallery"),
    path("timeline/", TimelineView.as_view(), name="timeline"),
    path("bv/", BvView.as_view(), name="bv"),
    path("apology/", ApologyView.as_view(), name="apology"),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
