import json
from datetime import datetime, date
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator

from apps.core.models import SiteSettings, ActivityLog
from apps.doctors.models import DoctorProfile
from apps.clinics.models import ClinicBranch
from apps.services.models import MedicalService, ServiceCategory
from apps.education.models import EducationalSeries, EducationalVideo
from apps.blog.models import Article, ArticleCategory
from apps.appointments.models import Appointment
from apps.appointments.services import get_available_slots, create_appointment_request
from apps.contact.forms import ContactForm
from apps.seo.schema_helpers import get_physician_and_clinic_schema, get_article_schema


def home_view(request):
    settings = SiteSettings.get_settings()
    doctor = DoctorProfile.objects.filter(is_active=True).prefetch_related('educations', 'experiences').first()
    featured_services = MedicalService.objects.filter(is_active=True, is_featured=True).order_by('order')[:6]
    if not featured_services.exists():
        featured_services = MedicalService.objects.filter(is_active=True).order_by('order')[:6]
    
    educational_series = EducationalSeries.objects.filter(is_published=True)[:3]
    latest_articles = Article.objects.filter(is_published=True).select_related('category')[:3]
    branches = ClinicBranch.objects.filter(is_active=True)
    primary_branch = branches.filter(is_primary=True).first() or branches.first()

    context = {
        'page_title': f"{settings.doctor_name_ar} | {settings.clinic_name_ar}" if request.LANGUAGE_CODE == 'ar' else f"{settings.doctor_name_en} | {settings.clinic_name_en}",
        'doctor': doctor,
        'featured_services': featured_services,
        'qualifications': doctor.educations.all().order_by('order') if doctor else [],
        'distinctions': doctor.experiences.all().order_by('order') if doctor else [],
        'educational_series': educational_series,
        'latest_articles': latest_articles,
        'branches': branches,
        'primary_branch': primary_branch,
        'schema_markup': get_physician_and_clinic_schema(request),
    }
    return render(request, 'public/home.html', context)


def about_view(request):
    doctor = DoctorProfile.objects.filter(is_active=True).prefetch_related('educations', 'experiences').first()
    context = {
        'page_title': _('عن الدكتور محمد الصياد | استشاري جراحة العظام والمفاصل') if request.LANGUAGE_CODE == 'ar' else 'About Dr. Mohammed Al-Sayyad',
        'doctor': doctor,
        'schema_markup': get_physician_and_clinic_schema(request),
    }
    return render(request, 'public/about.html', context)


def qualifications_view(request):
    doctor = DoctorProfile.objects.filter(is_active=True).prefetch_related('educations').first()
    qualifications = doctor.educations.all().order_by('order') if doctor else []
    context = {
        'page_title': _('المؤهلات العلمية والأكاديمية | الدكتور محمد الصياد') if request.LANGUAGE_CODE == 'ar' else 'Academic Qualifications | Dr. Mohammed Al-Sayyad',
        'doctor': doctor,
        'qualifications': qualifications,
        'schema_markup': get_physician_and_clinic_schema(request),
    }
    return render(request, 'public/qualifications.html', context)


def expertise_view(request):
    doctor = DoctorProfile.objects.filter(is_active=True).prefetch_related('experiences').first()
    experiences = doctor.experiences.all().order_by('order') if doctor else []
    context = {
        'page_title': _('الخبرات المهنية والتميز الجراحي | الدكتور محمد الصياد') if request.LANGUAGE_CODE == 'ar' else 'Professional Expertise | Dr. Mohammed Al-Sayyad',
        'doctor': doctor,
        'experiences': experiences,
        'schema_markup': get_physician_and_clinic_schema(request),
    }
    return render(request, 'public/expertise.html', context)


def services_list_view(request):
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    selected_category_slug = request.GET.get('category')
    services_qs = MedicalService.objects.filter(is_active=True)

    if selected_category_slug:
        services_qs = services_qs.filter(category__slug=selected_category_slug)

    context = {
        'page_title': _('الخدمات الطبية وجراحة العظام'),
        'categories': categories,
        'services': services_qs,
        'selected_category': selected_category_slug,
    }
    return render(request, 'public/services_list.html', context)


def service_detail_view(request, slug):
    service = MedicalService.objects.filter(slug=slug, is_active=True).first()
    
    if not service:
        # Legacy slug redirects to maintain backwards compatibility
        LEGACY_SLUG_MAP = {
            'total-knee-replacement': 'knee-joint-replacement',
            'knee-replacement-surgery': 'knee-joint-replacement',
            'total-hip-replacement': 'hip-joint-replacement',
            'knee-arthroscopy': 'general-orthopedic-surgery',
            'acl-reconstruction': 'general-orthopedic-surgery',
            'complex-fracture-surgery': 'fractures-and-bone-injuries',
            'non-surgical-joint-therapies': 'assessment-osteoarthritis-joint-wear',
        }
        target_slug = LEGACY_SLUG_MAP.get(slug)
        if target_slug:
            target_service = MedicalService.objects.filter(slug=target_slug, is_active=True).first()
            if target_service:
                return redirect(target_service.get_absolute_url(), permanent=True)

        # If the service exists in database but is inactive, allow staff preview or redirect to services list
        inactive_service = MedicalService.objects.filter(slug=slug).first()
        if inactive_service:
            if request.user.is_authenticated and request.user.is_staff:
                service = inactive_service
            else:
                return redirect('public:services')
        else:
            raise Http404(_("الخدمة الطبية المطلوبة غير موجودة."))

    related_services = MedicalService.objects.filter(is_active=True).exclude(id=service.id)
    if service.category:
        related_services = related_services.filter(category=service.category)
    related_services = related_services[:3]

    branches = ClinicBranch.objects.filter(is_active=True)

    context = {
        'page_title': service.title_ar if request.LANGUAGE_CODE == 'ar' else service.title_en,
        'meta_desc': service.meta_desc_ar if request.LANGUAGE_CODE == 'ar' else service.meta_desc_en,
        'service': service,
        'related_services': related_services,
        'branches': branches,
    }
    return render(request, 'public/service_detail.html', context)


def education_list_view(request):
    series_list = EducationalSeries.objects.filter(is_published=True).prefetch_related('videos')
    latest_videos = EducationalVideo.objects.filter(is_published=True).select_related('series')[:6]

    context = {
        'page_title': _('المكتبة التثقيفية وسلسلة الفيديوهات الطبية'),
        'series_list': series_list,
        'latest_videos': latest_videos,
    }
    return render(request, 'public/education_list.html', context)


def series_detail_view(request, slug):
    series = get_object_or_404(EducationalSeries, slug=slug, is_published=True)
    videos = series.videos.filter(is_published=True).order_by('episode_number')
    
    selected_video_id = request.GET.get('v')
    selected_video = None
    if selected_video_id:
        selected_video = videos.filter(id=selected_video_id).first()
    if not selected_video:
        selected_video = videos.first()

    context = {
        'page_title': series.title_ar if request.LANGUAGE_CODE == 'ar' else series.title_en,
        'series': series,
        'videos': videos,
        'current_video': selected_video,
    }
    return render(request, 'public/series_detail.html', context)


def blog_list_view(request):
    articles_qs = Article.objects.filter(is_published=True).select_related('category')
    categories = ArticleCategory.objects.filter(is_active=True)
    
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')

    if category_slug:
        articles_qs = articles_qs.filter(category__slug=category_slug)
    if search_query:
        articles_qs = articles_qs.filter(title_ar__icontains=search_query) | articles_qs.filter(content_ar__icontains=search_query)

    paginator = Paginator(articles_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': _('المقالات الطبية والنصائح الصحية'),
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'public/blog_list.html', context)


def article_detail_view(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Increment views
    Article.objects.filter(id=article.id).update(view_count=article.view_count + 1)
    
    related_articles = Article.objects.filter(is_published=True).exclude(id=article.id)
    if article.category:
        related_articles = related_articles.filter(category=article.category)
    related_articles = related_articles[:3]

    context = {
        'page_title': article.title_ar if request.LANGUAGE_CODE == 'ar' else article.title_en,
        'meta_desc': article.meta_desc_ar if request.LANGUAGE_CODE == 'ar' else article.meta_desc_en,
        'article': article,
        'related_articles': related_articles,
        'schema_markup': get_article_schema(article, request),
    }
    return render(request, 'public/article_detail.html', context)


def check_rate_limit(request, action_key: str, max_requests: int = 5, timeout_seconds: int = 600) -> bool:
    """
    In-memory / cache rate limiter based on client IP.
    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '127.0.0.1')
    cache_key = f"rate_limit:{action_key}:{ip}"
    current_count = cache.get(cache_key, 0)
    if current_count >= max_requests:
        return False
    cache.set(cache_key, current_count + 1, timeout=timeout_seconds)
    return True


def booking_view(request):
    branches = ClinicBranch.objects.filter(is_active=True)
    services = MedicalService.objects.filter(is_active=True)
    
    initial_service_id = request.GET.get('service')
    selected_service = None
    if initial_service_id:
        selected_service = services.filter(id=initial_service_id).first()

    if request.method == 'POST':
        # Honeypot spam protection
        if request.POST.get('website_hp'):
            return redirect('public:booking')

        # Rate limiting: max 5 bookings per 10 minutes per IP
        if not check_rate_limit(request, 'booking_submit', max_requests=5, timeout_seconds=600):
            messages.error(request, _('تم تجاوز الحد المسموح من المحاولات المؤقتة. يرجى الانتظار بضع دقائق قبل المحاولة مجدداً.'))
            return redirect('public:booking')

        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        branch_id = request.POST.get('branch')
        service_id = request.POST.get('service')
        appointment_date_str = request.POST.get('appointment_date', '').strip()
        appointment_time_str = request.POST.get('appointment_time', '').strip()
        visit_reason = request.POST.get('visit_reason', '').strip()
        patient_notes = request.POST.get('patient_notes', '').strip()

        # If no branch_id supplied, fall back to primary branch automatically
        if not branch_id:
            primary = ClinicBranch.objects.filter(is_active=True, is_primary=True).first() or ClinicBranch.objects.filter(is_active=True).first()
            if primary:
                branch_id = str(primary.id)

        # Validation
        if not full_name or not phone_number or not branch_id or not appointment_date_str or not appointment_time_str:
            messages.error(request, _('يرجى تعبئة كافة الحقول المطلوبة (الاسم، الهاتف، التاريخ، والوقت).'))
            return redirect('public:booking')

        branch = get_object_or_404(ClinicBranch, id=branch_id, is_active=True)
        service = services.filter(id=service_id).first() if service_id else None

        try:
            apt_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            apt_time = datetime.strptime(appointment_time_str, '%H:%M:%S').time() if len(appointment_time_str.split(':')) == 3 else datetime.strptime(appointment_time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, _('تنسيق التاريخ أو الوقت غير صالح.'))
            return redirect('public:booking')

        # Create appointment
        try:
            appointment = create_appointment_request(
                full_name=full_name,
                phone_number=phone_number,
                branch=branch,
                appointment_date=apt_date,
                appointment_time=apt_time,
                email=email,
                service=service,
                visit_reason=visit_reason,
                patient_notes=patient_notes
            )
            # Log activity without leaking sensitive patient personal health data
            ActivityLog.objects.create(
                action='حجز موعد جديد',
                target_model='Appointment',
                target_id=str(appointment.id),
                details=f"طلب حجز موعد جديد برمز مرجعي {appointment.booking_reference} وتاريخ {appointment_date_str}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return redirect('public:booking_success', booking_ref=appointment.booking_reference)
        except ValidationError as e:
            msg = e.message if hasattr(e, 'message') else str(e)
            messages.error(request, msg)
            return redirect('public:booking')
        except Exception as e:
            messages.error(request, f"{_('حدث خطأ أثناء تسجيل طلب الحجز:')} {str(e)}")
            return redirect('public:booking')

    primary_branch = ClinicBranch.objects.filter(is_active=True, is_primary=True).first() or branches.first()
    context = {
        'page_title': _('حجز موعد طبي - عيادة الدكتور محمد الصياد'),
        'branches': branches,
        'services': services,
        'selected_service': selected_service,
        'today_str': date.today().isoformat(),
        'primary_branch_id': primary_branch.id if primary_branch else '',
    }
    return render(request, 'public/booking.html', context)


def booking_success_view(request, booking_ref):
    appointment = get_object_or_404(Appointment, booking_id__startswith=booking_ref.replace('APT-', '').lower())
    context = {
        'page_title': _('تم استلام طلب الحجز بنجاح'),
        'appointment': appointment,
    }
    return render(request, 'public/booking_success.html', context)


def booking_status_view(request):
    appointment = None
    masked_name = ""
    searched = False
    query_ref = request.GET.get('ref', '').strip()
    query_phone = request.GET.get('phone', '').strip()

    if query_ref or query_phone:
        searched = True
        # SECURITY & PRIVACY HARDENING:
        # Require BOTH an exact/full booking reference (minimum 8 chars) AND matching phone number.
        # This prevents phone enumeration, random guessing, and patient record leaks.
        if not query_ref or not query_phone or len(query_ref) < 8:
            messages.warning(request, _('لأسباب تتعلق بحماية خصوصية المرضى، يلزم إدخال رمز الحجز كاملاً ورقم الهاتف المسجل معاً.'))
        else:
            clean_ref = query_ref.upper().replace('APT-', '').strip().lower()
            apt = Appointment.objects.select_related('patient', 'branch', 'service').filter(
                booking_id__startswith=clean_ref,
                patient__phone_number=query_phone
            ).first()

            if apt:
                appointment = apt
                # Mask patient name for privacy: e.g. "أحمد محمد علي" -> "أحمد م. ع."
                name_parts = apt.patient.full_name.strip().split()
                if len(name_parts) > 1:
                    masked_name = name_parts[0] + " " + " ".join([p[0] + "." for p in name_parts[1:]])
                else:
                    masked_name = name_parts[0]
            else:
                appointment = None

    context = {
        'page_title': _('متابعة حالة حجز الموعد'),
        'appointment': appointment,
        'masked_name': masked_name,
        'searched': searched,
        'query_ref': query_ref,
        'query_phone': query_phone,
    }
    return render(request, 'public/booking_status.html', context)


@require_GET
def api_available_slots(request):
    branch_id = request.GET.get('branch_id')
    date_str = request.GET.get('date')

    if not branch_id or not date_str:
        return JsonResponse({'status': 'error', 'message': _('بيانات الفرع أو التاريخ مفقودة')}, status=400)

    try:
        branch = ClinicBranch.objects.get(id=branch_id, is_active=True)
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ClinicBranch.DoesNotExist, ValueError):
        return JsonResponse({'status': 'error', 'message': _('فرع غير صالح أو تنسيق تاريخ غير صحيح')}, status=400)

    data = get_available_slots(branch, target_date)
    return JsonResponse({
        'status': 'success',
        'is_open': data['is_open'],
        'reason': data['reason'],
        'slots': data['slots']
    })


def contact_view(request):
    branches = ClinicBranch.objects.filter(is_active=True)
    primary_branch = branches.filter(is_primary=True).first() or branches.first()

    if request.method == 'POST':
        # Honeypot spam protection
        if request.POST.get('website_hp'):
            return redirect('public:contact')

        # Rate limiting: max 5 messages per 10 minutes per IP
        if not check_rate_limit(request, 'contact_submit', max_requests=5, timeout_seconds=600):
            messages.error(request, _('تم تجاوز الحد المسموح من الرسائل. يرجى الانتظار بضع دقائق قبل إرسال رسالة أخرى.'))
            return redirect('public:contact')

        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save(commit=False)
            contact_msg.ip_address = request.META.get('REMOTE_ADDR')
            contact_msg.save()
            messages.success(request, _('شكراً لتواصلك معنا. تم استلام رسالتك وسنقوم بالرد عليك في أقرب وقت.'))
            return redirect('public:contact')
        else:
            messages.error(request, _('يرجى تصحيح الأخطاء أدناه والمحاولة مجدداً.'))
    else:
        form = ContactForm()

    context = {
        'page_title': _('اتصل بنا - عيادة الدكتور محمد الصياد'),
        'form': form,
        'branches': branches,
        'primary_branch': primary_branch,
    }
    return render(request, 'public/contact.html', context)

