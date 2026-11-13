import json
from django.utils.safestring import mark_safe
from apps.core.models import SiteSettings
from apps.doctors.models import DoctorProfile
from apps.clinics.models import ClinicBranch


def get_physician_and_clinic_schema(request):
    """
    Returns Schema.org JSON-LD for Physician + MedicalClinic.
    """
    settings = SiteSettings.get_settings()
    doctor = DoctorProfile.objects.filter(is_active=True).first()
    branch = ClinicBranch.objects.filter(is_primary=True, is_active=True).first()

    base_url = request.build_absolute_uri('/')[:-1]

    data = {
        "@context": "https://schema.org",
        "@type": ["MedicalClinic", "Physician"],
        "name": settings.clinic_name_ar,
        "alternateName": settings.clinic_name_en,
        "url": base_url,
        "telephone": settings.phone,
        "medicalSpecialty": [
            "OrthopedicSurgery",
            "TraumaSurgery",
            "PelvicSurgery",
            "JointReplacement"
        ],
        "founder": {
            "@type": "Person",
            "name": doctor.name_ar if doctor else settings.doctor_name_ar,
            "jobTitle": doctor.title_ar if doctor else settings.specialty_ar,
            "worksFor": {
                "@type": "MedicalClinic",
                "name": settings.clinic_name_ar
            }
        },
        "address": {
            "@type": "PostalAddress",
            "streetAddress": branch.address_ar if branch else settings.address_ar,
            "addressLocality": "صنعاء (Sana'a)",
            "addressCountry": "YE"
        }
    }
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


def get_article_schema(article, request):
    """
    Returns Schema.org JSON-LD for MedicalWebPage / Article.
    """
    settings = SiteSettings.get_settings()
    article_url = request.build_absolute_uri(article.get_absolute_url())

    data = {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "headline": article.title_ar,
        "url": article_url,
        "datePublished": article.published_at.isoformat(),
        "dateModified": article.updated_at.isoformat(),
        "description": article.excerpt_ar,
        "author": {
            "@type": "Person",
            "name": settings.doctor_name_ar
        },
        "publisher": {
            "@type": "MedicalClinic",
            "name": settings.clinic_name_ar
        }
    }
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')

