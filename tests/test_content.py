from django.test import TestCase
from apps.services.models import ServiceCategory, MedicalService
from apps.education.models import (
    EducationalSeries,
    EducationalVideo,
    extract_youtube_id,
    detect_video_platform,
    build_facebook_embed_url
)
from apps.blog.models import ArticleCategory, Article


class ContentManagementTests(TestCase):
    def test_youtube_id_extractor(self):
        urls = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        for url, expected in urls:
            self.assertEqual(extract_youtube_id(url), expected)

    def test_video_platform_detection_and_facebook_embed(self):
        fb_urls = [
            "https://www.facebook.com/share/v/1EypS8H6SB/",
            "https://fb.watch/xyz123/",
            "https://www.facebook.com/DrAlSayyad/videos/1015849382910/",
        ]
        yt_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
        ]
        for u in fb_urls:
            self.assertEqual(detect_video_platform(u), 'facebook')
        for u in yt_urls:
            self.assertEqual(detect_video_platform(u), 'youtube')

        fb_embed = build_facebook_embed_url("https://www.facebook.com/share/v/1EypS8H6SB/")
        self.assertIn("facebook.com/plugins/video.php", fb_embed)
        self.assertIn("1EypS8H6SB", fb_embed)

    def test_educational_video_facebook_and_youtube_support(self):
        series = EducationalSeries.objects.create(
            title_ar='سلسلة التوعية الطبية',
            title_en='Medical Awareness Series',
            description_ar='وصف تجريبي',
            description_en='Test Description'
        )
        fb_video = EducationalVideo.objects.create(
            series=series,
            title_ar='فيديو فيسبوك توعوي',
            title_en='Facebook Educational Video',
            video_url='https://www.facebook.com/share/v/1EypS8H6SB/',
            episode_number=1
        )
        self.assertTrue(fb_video.is_facebook)
        self.assertFalse(fb_video.is_youtube)
        self.assertEqual(fb_video.video_platform, 'facebook')
        self.assertIn('facebook.com/plugins/video.php', fb_video.embed_url)

        yt_video = EducationalVideo.objects.create(
            series=series,
            title_ar='فيديو يوتيوب توعوي',
            title_en='YouTube Educational Video',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            episode_number=2
        )
        self.assertTrue(yt_video.is_youtube)
        self.assertFalse(yt_video.is_facebook)
        self.assertEqual(yt_video.video_platform, 'youtube')
        self.assertIn('youtube-nocookie.com/embed/dQw4w9WgXcQ', yt_video.embed_url)

    def test_article_creation_and_reading_time(self):
        cat = ArticleCategory.objects.create(name_ar='العظام', name_en='Orthopedics')
        content_text = "كلمة " * 400  # 400 words = approx 2 minutes reading
        article = Article.objects.create(
            category=cat,
            title_ar='مقال تجريبي عن صحة المفاصل',
            title_en='Test Article on Joints',
            excerpt_ar='موجز تجريبي',
            excerpt_en='Test excerpt',
            content_ar=content_text,
            content_en='Short English summary',
            is_published=True
        )
        self.assertGreaterEqual(article.reading_time, 2)
        self.assertTrue(len(article.slug) > 0)
        self.assertIn('تنبيه طبي', article.medical_disclaimer_ar)

    def test_service_creation_and_meta(self):
        service = MedicalService.objects.create(
            title_ar='تنظير الركبة المتطور',
            title_en='Advanced Knee Arthroscopy',
            short_desc_ar='شرح مختصر للخدمة',
            short_desc_en='Short description of service',
            full_desc_ar='شرح تفصيلي موسع',
            full_desc_en='Detailed description'
        )
        self.assertEqual(service.slug, 'advanced-knee-arthroscopy')
        self.assertIn('الدكتور محمد الصياد', service.meta_title_ar)

