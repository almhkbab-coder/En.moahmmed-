from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.cache import cache

from apps.core.models import SiteSettings, ActivityLog
from apps.doctors.models import DoctorProfile, Education, Experience, Certificate
from apps.clinics.models import ClinicBranch, WorkingHours, ClinicHoliday
from apps.services.models import MedicalService, ServiceCategory
from apps.education.models import EducationalSeries, EducationalVideo
from apps.blog.models import Article, ArticleCategory
from apps.appointments.models import Appointment, Patient, AppointmentStatusHistory
from apps.appointments.services import update_appointment_status_safe
from apps.contact.models import ContactMessage
from .forms import DoctorProfileForm, MedicalServiceForm, EducationalSeriesForm, EducationalVideoForm, ArticleForm, SiteSettingsForm
from .decorators import (
    super_admin_only,
    doctor_or_admin_required,
    appointment_staff_required,
    content_staff_required
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1')).split(',')[0].strip()

    if request.method == 'POST':
        username_val = request.POST.get('username', '').strip()
        password_val = request.POST.get('password', '')

        # Brute force lockout check
        lockout_key = f"login_fail_lock_{client_ip}_{username_val}"
        failed_attempts = cache.get(lockout_key, 0)
        if failed_attempts >= 5:
            messages.error(request, _('تم حظر تسجيل الدخول مؤقتاً لمدة 15 دقيقة بسبب تكرار المحاولات الخاطئة كإجراء أمني.'))
            return render(request, 'dashboard/login.html', {'page_title': _('تسجيل الدخول إلى لوحة التحكم')}, status=429)

        user = authenticate(request, username=username_val, password=password_val)
        if user is not None:
            if user.is_active:
                login(request, user)
                cache.delete(lockout_key)
                ActivityLog.objects.create(
                    user=user,
                    action='تسجيل دخول لوحة التحكم',
                    target_model='User',
                    target_id=str(user.id),
                    details=f"تسجيل دخول ناجح للمستخدم {user.username}",
                    ip_address=client_ip
                )
                messages.success(request, f"{_('مرحباً بك يا')} {user.get_full_name() or user.username}")
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, _('هذا الحساب معطل. يرجى التواصل مع مسؤول النظام.'))
        else:
            cache.set(lockout_key, failed_attempts + 1, timeout=900)
            remaining = max(0, 5 - (failed_attempts + 1))
            messages.error(request, f"{_('اسم المستخدم أو كلمة المرور غير صحيحة.')} ({_('المحاولات المتبقية:')} {remaining})")

    return render(request, 'dashboard/login.html', {'page_title': _('تسجيل الدخول إلى لوحة التحكم')})


@login_required
def logout_view(request):
    ActivityLog.objects.create(
        user=request.user,
        action='تسجيل خروج',
        target_model='User',
        target_id=str(request.user.id),
        details=f"تسجيل خروج المستخدم {request.user.username}",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    logout(request)
    messages.info(request, _('تم تسجيل الخروج بنجاح.'))
    return redirect('dashboard:login')


@login_required
def dashboard_index(request):
    # Real database statistics
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status=Appointment.Status.PENDING).count()
    confirmed_appointments = Appointment.objects.filter(status=Appointment.Status.CONFIRMED).count()
    completed_appointments = Appointment.objects.filter(status=Appointment.Status.COMPLETED).count()
    cancelled_appointments = Appointment.objects.filter(status__in=[Appointment.Status.CANCELLED, Appointment.Status.REJECTED]).count()

    total_patients = Patient.objects.count()
    total_services = MedicalService.objects.count()
    total_articles = Article.objects.count()
    total_videos = EducationalVideo.objects.count()
    total_series = EducationalSeries.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    # Recent 6 appointment requests
    recent_appointments = Appointment.objects.select_related('patient', 'branch', 'service').order_by('-created_at')[:6]

    # Chart 1: Status distribution data
    status_counts = [
        pending_appointments,
        confirmed_appointments,
        completed_appointments,
        cancelled_appointments
    ]

    # Chart 2: Last 6 months trend
    now = timezone.now()
    month_labels = []
    month_counts = []
    for i in range(5, -1, -1):
        # Calculate month
        first_day_of_month = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        next_month = (first_day_of_month + timedelta(days=32)).replace(day=1)
        cnt = Appointment.objects.filter(created_at__gte=first_day_of_month, created_at__lt=next_month).count()
        month_labels.append(first_day_of_month.strftime('%b %Y'))
        month_counts.append(cnt)

    today_date = timezone.localdate()
    today_appointments = Appointment.objects.filter(appointment_date=today_date).count()
    doctor_profile = DoctorProfile.objects.first()

    context = {
        'page_title': _('لوحة التحكم والإحصائيات العامة'),
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'doctor_profile': doctor_profile,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_patients': total_patients,
        'total_services': total_services,
        'total_articles': total_articles,
        'total_videos': total_videos,
        'total_series': total_series,
        'unread_messages': unread_messages,
        'recent_appointments': recent_appointments,
        'status_counts': status_counts,
        'month_labels': month_labels,
        'month_counts': month_counts,
    }
    return render(request, 'dashboard/index.html', context)


# ==========================================
# APPOINTMENTS MANAGEMENT
# ==========================================
@login_required
@appointment_staff_required
def appointments_list(request):
    qs = Appointment.objects.select_related('patient', 'branch', 'service').order_by('-appointment_date', '-appointment_time')

    # Filters
    status_filter = request.GET.get('status')
    branch_filter = request.GET.get('branch')
    date_filter = request.GET.get('date')
    search_query = request.GET.get('q')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if branch_filter:
        qs = qs.filter(branch_id=branch_filter)
    if date_filter:
        qs = qs.filter(appointment_date=date_filter)
    if search_query:
        from apps.core.encryption import compute_search_token
        token = compute_search_token(search_query)
        clean_ref = search_query.upper().replace('APT-', '').strip().lower()
        qs = qs.filter(
            Q(patient__name_search_token=token) |
            Q(patient__phone_number__icontains=search_query) |
            Q(booking_id__startswith=clean_ref)
        )

    branches = ClinicBranch.objects.filter(is_active=True)
    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_title': _('إدارة المواعيد وحجوزات المرضى'),
        'page_obj': page_obj,
        'branches': branches,
        'status_choices': Appointment.Status.choices,
        'selected_status': status_filter,
        'selected_branch': branch_filter,
        'selected_date': date_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/appointments_list.html', context)


@login_required
@appointment_staff_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'branch', 'service').prefetch_related('status_history__changed_by'),
        pk=pk
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        new_status = request.POST.get('new_status')
        staff_notes = request.POST.get('staff_notes', '').strip()

        if new_status and new_status in dict(Appointment.Status.choices):
            try:
                update_appointment_status_safe(
                    appointment_id=appointment.id,
                    new_status=new_status,
                    staff_user=request.user,
                    notes=staff_notes
                )
                ActivityLog.objects.create(
                    user=request.user,
                    action='تحديث حالة موعد',
                    target_model='Appointment',
                    target_id=str(appointment.id),
                    details=f"تغيير حالة حجز {appointment.booking_reference} إلى {new_status}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, _('تم تحديث حالة الموعد بنجاح.'))
            except Exception as e:
                messages.error(request, str(e))
            return redirect('dashboard:appointment_detail', pk=appointment.id)

    context = {
        'page_title': f"{_('تفاصيل الحجز')} {appointment.booking_reference}",
        'appointment': appointment,
        'status_choices': Appointment.Status.choices,
    }
    return render(request, 'dashboard/appointment_detail.html', context)


@login_required
@appointment_staff_required
def appointments_calendar(request):
    """
    Calendar overview for upcoming days.
    Optimized single database query instead of 14 separate N+1 queries.
    """
    today = timezone.localdate()
    days_ahead = 14
    dates_list = [today + timedelta(days=i) for i in range(days_ahead)]
    
    appointments_by_date = {d: [] for d in dates_list}
    all_apts = Appointment.objects.filter(
        appointment_date__gte=dates_list[0],
        appointment_date__lte=dates_list[-1]
    ).select_related('patient', 'branch', 'service').order_by('appointment_time')

    for apt in all_apts:
        if apt.appointment_date in appointments_by_date:
            appointments_by_date[apt.appointment_date].append(apt)

    context = {
        'page_title': _('جدول المواعيد والتقويم السريري'),
        'appointments_by_date': appointments_by_date,
    }
    return render(request, 'dashboard/appointments_calendar.html', context)


# ==========================================
# PATIENTS DIRECTORY
# ==========================================
@login_required
@appointment_staff_required
def patients_list(request):
    search_query = request.GET.get('q', '').strip()
    qs = Patient.objects.annotate(appointment_count=Count('appointments')).order_by('-created_at')

    if search_query:
        from apps.core.encryption import compute_search_token
        token = compute_search_token(search_query)
        qs = qs.filter(
            Q(name_search_token=token) |
            Q(phone_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_title': _('سجلات المرضى'),
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'dashboard/patients_list.html', context)


@login_required
@appointment_staff_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = patient.appointments.select_related('branch', 'service').order_by('-appointment_date', '-appointment_time')

    if request.method == 'POST':
        patient.full_name = request.POST.get('full_name', patient.full_name).strip()
        patient.phone_number = request.POST.get('phone_number', patient.phone_number).strip()
        patient.email = request.POST.get('email', patient.email).strip() or None
        patient.notes = request.POST.get('notes', patient.notes).strip()
        patient.save()
        messages.success(request, _('تم تحديث بيانات المريض بنجاح.'))
        return redirect('dashboard:patient_detail', pk=patient.id)

    context = {
        'page_title': f"{_('ملف المريض:')} {patient.full_name}",
        'patient': patient,
        'appointments': appointments,
    }
    return render(request, 'dashboard/patient_detail.html', context)


# ==========================================
# MEDICAL SERVICES CRUD
# ==========================================
@login_required
@content_staff_required
def services_list(request):
    services = MedicalService.objects.select_related('category').order_by('order', 'id')
    context = {
        'page_title': _('إدارة الخدمات الطبية والعمليات الجراحية'),
        'services': services,
    }
    return render(request, 'dashboard/services_list.html', context)


@login_required
@content_staff_required
def service_create(request):
    if request.method == 'POST':
        form = MedicalServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='إضافة خدمة طبية جديدة',
                target_model='MedicalService',
                target_id=str(service.id),
                details=f"إضافة {service.title_ar}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, _('تمت إضافة الخدمة الطبية بنجاح.'))
            return redirect('dashboard:services_list')
    else:
        form = MedicalServiceForm()

    context = {
        'page_title': _('إضافة خدمة طبية جديدة'),
        'form': form,
    }
    return render(request, 'dashboard/service_form.html', context)


@login_required
@content_staff_required
def service_edit(request, pk):
    service = get_object_or_404(MedicalService, pk=pk)
    if request.method == 'POST':
        form = MedicalServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='تعديل خدمة طبية',
                target_model='MedicalService',
                target_id=str(service.id),
                details=f"تعديل {service.title_ar}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, _('تم تحديث الخدمة الطبية بنجاح.'))
            return redirect('dashboard:services_list')
    else:
        form = MedicalServiceForm(instance=service)

    context = {
        'page_title': f"{_('تعديل الخدمة:')} {service.title_ar}",
        'form': form,
        'service': service,
    }
    return render(request, 'dashboard/service_form.html', context)


@login_required
@content_staff_required
def service_delete(request, pk):
    service = get_object_or_404(MedicalService, pk=pk)
    if request.method == 'POST':
        service_title = service.title_ar
        service.delete()
        ActivityLog.objects.create(
            user=request.user,
            action='حذف خدمة طبية',
            target_model='MedicalService',
            target_id=str(pk),
            details=f"حذف {service_title}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, _('تم حذف الخدمة الطبية بنجاح.'))
        return redirect('dashboard:services_list')
    return render(request, 'dashboard/confirm_delete.html', {
        'page_title': _('تأكيد حذف الخدمة الطبية'),
        'item_title': service.title_ar,
        'cancel_url': 'dashboard:services_list'
    })


# ==========================================
# EDUCATIONAL SERIES & VIDEOS CRUD
# ==========================================
@login_required
@content_staff_required
def education_series_list(request):
    series_list = EducationalSeries.objects.annotate(video_count=Count('videos')).order_by('order', '-created_at')
    context = {
        'page_title': _('إدارة السلاسل والفيديوهات التثقيفية'),
        'series_list': series_list,
    }
    return render(request, 'dashboard/education_series_list.html', context)


@login_required
@content_staff_required
def series_create(request):
    if request.method == 'POST':
        form = EducationalSeriesForm(request.POST, request.FILES)
        if form.is_valid():
            series = form.save()
            messages.success(request, _('تمت إضافة السلسلة التوعوية بنجاح.'))
            return redirect('dashboard:education_series_list')
    else:
        form = EducationalSeriesForm()
    return render(request, 'dashboard/series_form.html', {'form': form, 'page_title': _('إضافة سلسلة توعوية جديدة')})


@login_required
@content_staff_required
def series_edit(request, pk):
    series = get_object_or_404(EducationalSeries, pk=pk)
    videos = series.videos.all().order_by('episode_number')
    if request.method == 'POST':
        form = EducationalSeriesForm(request.POST, request.FILES, instance=series)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث السلسلة التوعوية بنجاح.'))
            return redirect('dashboard:education_series_list')
    else:
        form = EducationalSeriesForm(instance=series)
    return render(request, 'dashboard/series_form.html', {'form': form, 'series': series, 'videos': videos, 'page_title': f"{_('تعديل')} {series.title_ar}"})


@login_required
@content_staff_required
def video_create(request):
    series_id = request.GET.get('series')
    initial_data = {}
    if series_id:
        initial_data['series'] = series_id

    if request.method == 'POST':
        form = EducationalVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            messages.success(request, _('تمت إضافة الفيديو التثقيفي بنجاح.'))
            return redirect('dashboard:series_edit', pk=video.series.id)
    else:
        form = EducationalVideoForm(initial=initial_data)

    return render(request, 'dashboard/video_form.html', {'form': form, 'page_title': _('إضافة حلقة / فيديو تثقيفي جديد')})


@login_required
@content_staff_required
def video_edit(request, pk):
    video = get_object_or_404(EducationalVideo, pk=pk)
    if request.method == 'POST':
        form = EducationalVideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث الفيديو التثقيفي بنجاح.'))
            return redirect('dashboard:series_edit', pk=video.series.id)
    else:
        form = EducationalVideoForm(instance=video)

    return render(request, 'dashboard/video_form.html', {'form': form, 'video': video, 'page_title': f"{_('تعديل فيديو:')} {video.title_ar}"})


@login_required
@content_staff_required
def video_delete(request, pk):
    video = get_object_or_404(EducationalVideo, pk=pk)
    series_id = video.series.id
    if request.method == 'POST':
        video.delete()
        messages.success(request, _('تم حذف الفيديو بنجاح.'))
        return redirect('dashboard:series_edit', pk=series_id)
    return render(request, 'dashboard/confirm_delete.html', {
        'page_title': _('تأكيد حذف الفيديو'),
        'item_title': video.title_ar,
        'cancel_url': 'dashboard:series_edit',
        'cancel_pk': series_id
    })


# ==========================================
# ARTICLES (BLOG) CRUD
# ==========================================
@login_required
@content_staff_required
def articles_list(request):
    articles = Article.objects.select_related('category', 'author').order_by('-published_at', '-created_at')
    context = {
        'page_title': _('إدارة المقالات الطبية والنصائح'),
        'articles': articles,
    }
    return render(request, 'dashboard/articles_list.html', context)


@login_required
@content_staff_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, _('تم حفظ المقال الطبي بنجاح.'))
            return redirect('dashboard:articles_list')
    else:
        form = ArticleForm()

    return render(request, 'dashboard/article_form.html', {'form': form, 'page_title': _('كتابة مقال طبي جديد')})


@login_required
@content_staff_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث المقال بنجاح.'))
            return redirect('dashboard:articles_list')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'dashboard/article_form.html', {'form': form, 'article': article, 'page_title': f"{_('تعديل مقال:')} {article.title_ar}"})


@login_required
@content_staff_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, _('تم حذف المقال بنجاح.'))
        return redirect('dashboard:articles_list')
    return render(request, 'dashboard/confirm_delete.html', {
        'page_title': _('تأكيد حذف المقال'),
        'item_title': article.title_ar,
        'cancel_url': 'dashboard:articles_list'
    })


# ==========================================
# DOCTOR PROFILE MANAGEMENT
# ==========================================
@login_required
@doctor_or_admin_required
def doctor_profile_edit(request):
    profile, created = DoctorProfile.objects.get_or_create(id=1)
    educations = profile.educations.all()
    experiences = profile.experiences.all()
    certificates = profile.certificates.all()

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='تحديث ملف الطبيب',
                target_model='DoctorProfile',
                target_id=str(profile.id),
                details="تحديث السيرة الذاتية والمعلومات الرسمية للطبيب",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, _('تم تحديث الملف المهني للطبيب بنجاح.'))
            return redirect('dashboard:doctor_profile')
    else:
        form = DoctorProfileForm(instance=profile)

    context = {
        'page_title': _('إدارة الملف المهني والسيرة الذاتية للطبيب'),
        'form': form,
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'certificates': certificates,
    }
    return render(request, 'dashboard/doctor_profile.html', context)


# ==========================================
# SETTINGS & CONTACT MESSAGES & AUDIT LOGS
# ==========================================
@login_required
@super_admin_only
def site_settings_edit(request):
    settings_obj = SiteSettings.get_settings()
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='تحديث إعدادات الموقع',
                target_model='SiteSettings',
                target_id='1',
                details="تحديث بيانات العيادة وأرقام التواصل وشبكات التواصل",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, _('تم تحديث إعدادات النظام بنجاح.'))
            return redirect('dashboard:site_settings')
    else:
        form = SiteSettingsForm(instance=settings_obj)

    return render(request, 'dashboard/site_settings.html', {'form': form, 'page_title': _('إعدادات الموقع والنظام')})


@login_required
@appointment_staff_required
def contact_messages_list(request):
    messages_qs = ContactMessage.objects.all().order_by('-created_at')
    # Mark all unread as read on visit or by detail
    ContactMessage.objects.filter(is_read=False).update(is_read=True)

    paginator = Paginator(messages_qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/contact_messages.html', {
        'page_title': _('استفسارات ورسائل التواصل'),
        'page_obj': page_obj,
    })


@login_required
@super_admin_only
def activity_logs_list(request):
    logs = ActivityLog.objects.select_related('user').order_by('-created_at')
    paginator = Paginator(logs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/activity_logs.html', {
        'page_title': _('سجل العمليات والرقابة الأمنية (Audit Logs)'),
        'page_obj': page_obj,
    })
