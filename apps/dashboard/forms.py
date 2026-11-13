from django import forms
from django.utils.translation import gettext_lazy as _
from apps.doctors.models import DoctorProfile, Education, Experience, Certificate
from apps.services.models import MedicalService, ServiceCategory
from apps.education.models import EducationalSeries, EducationalVideo
from apps.blog.models import Article, ArticleCategory
from apps.clinics.models import ClinicBranch, WorkingHours, ClinicHoliday
from apps.core.models import SiteSettings


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            'name_ar', 'name_en', 'title_ar', 'title_en',
            'specialty_ar', 'specialty_en', 'bio_ar', 'bio_en',
            'vision_ar', 'vision_en',
            'profile_photo', 'hero_photo', 'years_of_experience',
            'successful_surgeries', 'consultations_count', 'is_active'
        ]
        widgets = {
            'bio_ar': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'bio_en': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'vision_ar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'vision_en': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'


class MedicalServiceForm(forms.ModelForm):
    class Meta:
        model = MedicalService
        fields = [
            'category', 'title_ar', 'title_en', 'slug',
            'short_desc_ar', 'short_desc_en', 'full_desc_ar', 'full_desc_en',
            'featured_image', 'icon', 'is_featured', 'is_active', 'order',
            'meta_title_ar', 'meta_desc_ar'
        ]
        widgets = {
            'short_desc_ar': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'short_desc_en': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'full_desc_ar': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'full_desc_en': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'


class EducationalSeriesForm(forms.ModelForm):
    class Meta:
        model = EducationalSeries
        fields = ['title_ar', 'title_en', 'slug', 'description_ar', 'description_en', 'cover_image', 'is_published', 'order']
        widgets = {
            'description_ar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'description_en': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'


class EducationalVideoForm(forms.ModelForm):
    class Meta:
        model = EducationalVideo
        fields = [
            'series', 'title_ar', 'title_en', 'slug',
            'video_platform', 'video_url', 'custom_thumbnail',
            'duration_minutes', 'episode_number',
            'description_ar', 'description_en', 'is_published'
        ]
        widgets = {
            'video_platform': forms.Select(attrs={'class': 'form-select'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.facebook.com/... أو https://www.youtube.com/watch?v=...'}),
            'description_ar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'description_en': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if not self.initial.get('video_url'):
                self.initial['video_url'] = self.instance.watch_url
        self.fields['video_url'].required = True
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, (forms.Select, forms.FileInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'category', 'title_ar', 'title_en', 'slug',
            'excerpt_ar', 'excerpt_en', 'content_ar', 'content_en',
            'featured_image', 'is_published', 'published_at',
            'meta_title_ar', 'meta_desc_ar'
        ]
        widgets = {
            'excerpt_ar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'excerpt_en': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'content_ar': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            'content_en': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'clinic_name_ar', 'clinic_name_en', 'doctor_name_ar', 'doctor_name_en',
            'specialty_ar', 'specialty_en', 'phone', 'mobile', 'whatsapp', 'email',
            'address_ar', 'address_en', 'working_hours_summary_ar', 'working_hours_summary_en',
            'logo', 'favicon', 'facebook_url', 'x_url', 'youtube_url', 'instagram_url',
            'meta_title_ar', 'meta_description_ar'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'

