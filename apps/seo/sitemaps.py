from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.services.models import MedicalService
from apps.education.models import EducationalSeries
from apps.blog.models import Article


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return [
            'public:home',
            'public:about',
            'public:qualifications',
            'public:services',
            'public:expertise',
            'public:education',
            'public:blog',
            'public:booking',
            'public:contact',
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return MedicalService.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class SeriesSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return EducationalSeries.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ArticleSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

