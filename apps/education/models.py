import re
import uuid
import urllib.parse
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from apps.core.validators import validate_image_file


def extract_youtube_id(url):
    """
    Safely extract YouTube video ID from various URL patterns.
    """
    if not url:
        return ''
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    # If the input is already just an 11-char ID
    if re.match(r'^[0-9A-Za-z_-]{11}$', url.strip()):
        return url.strip()
    return ''


def detect_video_platform(url):
    """
    Detect whether the given video URL belongs to Facebook or YouTube.
    """
    if not url:
        return 'youtube'
    url_lower = url.lower()
    if any(k in url_lower for k in ['facebook.com', 'fb.watch', 'fb.com', 'fb.me']):
        return 'facebook'
    return 'youtube'


def build_facebook_embed_url(url):
    """
    Generate the official responsive Facebook Video Embed player URL.
    """
    if not url:
        return ''
    encoded_url = urllib.parse.quote(url.strip(), safe='')
    return f"https://www.facebook.com/plugins/video.php?href={encoded_url}&show_text=false&t=0"


class EducationalSeries(models.Model):
    title_ar = models.CharField(_('عنوان السلسلة (عربي)'), max_length=255)
    title_en = models.CharField(_('عنوان السلسلة (إنجليزي)'), max_length=255)
    slug = models.SlugField(_('الرابط اللطيف (Slug)'), max_length=255, unique=True, allow_unicode=True)
    description_ar = models.TextField(_('وصف السلسلة (عربي)'))
    description_en = models.TextField(_('وصف السلسلة (إنجليزي)'))
    cover_image = models.ImageField(_('غلاف السلسلة'), upload_to='education/series/', blank=True, null=True, validators=[validate_image_file])
    is_published = models.BooleanField(_('منشورة'), default=True)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('سلسلة توعوية / تثقيفية')
        verbose_name_plural = _('السلاسل التوعوية والتثقيفية')
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_en) or f"series-{uuid.uuid4().hex[:6]}"
            self.slug = base_slug
        super().save(*args, **kwargs)

    @property
    def episode_count(self):
        return self.videos.filter(is_published=True).count()

    def get_absolute_url(self):
        return reverse('public:series_detail', kwargs={'slug': self.slug})


class EducationalVideo(models.Model):
    PLATFORM_CHOICES = [
        ('youtube', _('يوتيوب (YouTube)')),
        ('facebook', _('فيسبوك (Facebook)')),
    ]

    series = models.ForeignKey(EducationalSeries, on_delete=models.CASCADE, related_name='videos', verbose_name=_('السلسلة التوعوية'))
    title_ar = models.CharField(_('عنوان الحلقة / الفيديو (عربي)'), max_length=255)
    title_en = models.CharField(_('عنوان الحلقة / الفيديو (إنجليزي)'), max_length=255)
    slug = models.SlugField(_('الرابط اللطيف (Slug)'), max_length=255, unique=True, allow_unicode=True)
    
    video_platform = models.CharField(_('منصة الفيديو'), max_length=20, choices=PLATFORM_CHOICES, default='youtube')
    video_url = models.URLField(_('رابط الفيديو (يوتيوب أو فيسبوك)'), max_length=500, blank=True, help_text=_('رابط فيديو يوتيوب أو فيسبوك كامل'))
    youtube_url = models.URLField(_('رابط الفيديو (متوافق)'), max_length=500, blank=True, help_text=_('رابط كامل مثل https://www.youtube.com/watch?v=... أو https://www.facebook.com/...'))
    youtube_video_id = models.CharField(_('معرف فيديو يوتيوب'), max_length=50, blank=True)
    custom_thumbnail = models.ImageField(_('صورة مصغرة مخصصة (اختياري)'), upload_to='education/thumbnails/', blank=True, null=True, validators=[validate_image_file])
    
    duration_minutes = models.PositiveIntegerField(_('مدة الفيديو (بالدقائق)'), default=5)
    episode_number = models.PositiveIntegerField(_('رقم الحلقة في السلسلة'), default=1)
    
    description_ar = models.TextField(_('شرح ونقاط الفيديو (عربي)'), blank=True)
    description_en = models.TextField(_('شرح ونقاط الفيديو (إنجليزي)'), blank=True)
    
    is_published = models.BooleanField(_('منشور'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('فيديو تثقيفي / حلقة')
        verbose_name_plural = _('الفيديوهات التثقيفية')
        ordering = ['series', 'episode_number', '-created_at']

    def __str__(self):
        return f"{self.series.title_ar} - حلقة {self.episode_number}: {self.title_ar}"

    def save(self, *args, **kwargs):
        effective_url = (self.video_url or self.youtube_url or '').strip()
        self.video_url = effective_url
        self.youtube_url = effective_url

        detected = detect_video_platform(effective_url)
        if not self.video_platform or self.video_platform not in ['youtube', 'facebook']:
            self.video_platform = detected
        elif detected == 'facebook':
            self.video_platform = 'facebook'

        if self.video_platform == 'youtube':
            self.youtube_video_id = extract_youtube_id(effective_url)
        else:
            self.youtube_video_id = ''

        if not self.slug:
            base_slug = slugify(self.title_en) or f"video-{uuid.uuid4().hex[:6]}"
            self.slug = base_slug
        super().save(*args, **kwargs)

    @property
    def watch_url(self):
        return self.video_url or self.youtube_url or ''

    @property
    def is_facebook(self):
        return self.video_platform == 'facebook' or detect_video_platform(self.watch_url) == 'facebook'

    @property
    def is_youtube(self):
        return not self.is_facebook

    @property
    def embed_url(self):
        url = self.watch_url
        if not url:
            return ""
        if self.is_facebook:
            return build_facebook_embed_url(url)
        if self.youtube_video_id:
            return f"https://www.youtube-nocookie.com/embed/{self.youtube_video_id}?rel=0"
        y_id = extract_youtube_id(url)
        if y_id:
            return f"https://www.youtube-nocookie.com/embed/{y_id}?rel=0"
        return ""

    @property
    def thumbnail_url(self):
        if self.custom_thumbnail:
            return self.custom_thumbnail.url
        if self.is_youtube and self.youtube_video_id:
            return f"https://img.youtube.com/vi/{self.youtube_video_id}/hqdefault.jpg"
        if self.series and self.series.cover_image:
            return self.series.cover_image.url
        return ""

