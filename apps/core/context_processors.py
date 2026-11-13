from django.utils import timezone
from django.utils.translation import get_language
from .models import SiteSettings


def site_settings_context(request):
    try:
        settings_obj = SiteSettings.get_settings()
    except Exception:
        settings_obj = None

    current_lang = get_language() or 'ar'
    is_rtl = current_lang == 'ar'

    return {
        'site_settings': settings_obj,
        'current_year': timezone.now().year,
        'current_lang': current_lang,
        'is_rtl': is_rtl,
    }

