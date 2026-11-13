from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from apps.seo.sitemaps import StaticViewSitemap, ServiceSitemap, SeriesSitemap, ArticleSitemap
from apps.seo.views import robots_txt

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'series': SeriesSitemap,
    'articles': ArticleSitemap,
}

urlpatterns = [
    # Administration
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # Internationalization language toggle
    path('i18n/', include('django.conf.urls.i18n')),

    # SEO & Crawlers
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),

    # Public Medical Website
    path('', include('apps.core.urls_public', namespace='public')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site headers
admin.site.site_header = "عيادة الصياد | جراحة العظام والمفاصل"
admin.site.site_title = "لوحة إدارة عيادة الصياد"
admin.site.index_title = "نظام إدارة العيادة وقواعد البيانات"

