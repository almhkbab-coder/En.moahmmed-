from datetime import datetime, date, time, timedelta
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import zoneinfo

from apps.clinics.models import ClinicBranch, WorkingHours, ClinicHoliday
from .models import Patient, Appointment, AppointmentStatusHistory

ADEN_TZ = zoneinfo.ZoneInfo("Asia/Aden")


def get_model_day_of_week(py_date: date) -> int:
    """
    Map Python date.weekday() (Monday=0 ... Sunday=6) to model DayOfWeek:
    0: Saturday, 1: Sunday, 2: Monday, 3: Tuesday, 4: Wednesday, 5: Thursday, 6: Friday
    """
    mapping = {
        5: 0,  # Saturday
        6: 1,  # Sunday
        0: 2,  # Monday
        1: 3,  # Tuesday
        2: 4,  # Wednesday
        3: 5,  # Thursday
        4: 6,  # Friday
    }
    return mapping[py_date.weekday()]


def format_time_arabic(t: time) -> str:
    hour = t.hour
    minute = t.minute
    suffix = "ص" if hour < 12 else "م"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour:02d}:{minute:02d} {suffix}"


def get_available_slots(branch: ClinicBranch, target_date: date):
    """
    Returns available and booked appointment slots for a given branch and date.
    """
    now_in_aden = datetime.now(ADEN_TZ)
    today_in_aden = now_in_aden.date()

    if target_date < today_in_aden:
        return {
            'is_open': False,
            'reason': _('التاريخ المحدد في الماضي ولا يمكن حجز موعد فيه'),
            'slots': []
        }

    if not branch.is_active:
        return {
            'is_open': False,
            'reason': _('الفرع المحدد غير متاح للحجوزات حالياً'),
            'slots': []
        }

    # Check for holiday
    holiday_exists = ClinicHoliday.objects.filter(
        date=target_date
    ).filter(
        models.Q(branch=branch) | models.Q(branch__isnull=True)
    ).first()

    if holiday_exists:
        return {
            'is_open': False,
            'reason': f"{_('عطلة رسمية بالعيادة:')} {holiday_exists.reason_ar}",
            'slots': []
        }

    # Check working hours
    model_day = get_model_day_of_week(target_date)
    working_hour = WorkingHours.objects.filter(branch=branch, day_of_week=model_day).first()

    if not working_hour or working_hour.is_closed:
        return {
            'is_open': False,
            'reason': _('العيادة مغلقة في هذا اليوم (عطلة أسبوعية)'),
            'slots': []
        }

    # Fetch already confirmed appointments on this date with their time intervals
    confirmed_apts = list(
        Appointment.objects.filter(
            branch=branch,
            appointment_date=target_date,
            status=Appointment.Status.CONFIRMED
        ).values('appointment_time', 'end_time', 'duration_minutes')
    )
    confirmed_intervals = []
    for c in confirmed_apts:
        c_start = c['appointment_time']
        c_end = c['end_time']
        if not c_end:
            c_end = (datetime.combine(target_date, c_start) + timedelta(minutes=c['duration_minutes'] or working_hour.slot_duration_minutes)).time()
        confirmed_intervals.append((c_start, c_end))

    slots = []
    slot_delta = timedelta(minutes=working_hour.slot_duration_minutes)

    # Helper generator
    def generate_shift_slots(start_t: time, end_t: time, shift_name: str, shift_label: str):
        if not start_t or not end_t:
            return
        current_dt = datetime.combine(target_date, start_t)
        end_dt = datetime.combine(target_date, end_t)
        while current_dt + slot_delta <= end_dt:
            t_val = current_dt.time()
            slot_end_val = (current_dt + slot_delta).time()

            # Interval overlap check: Slot [t_val, slot_end_val) overlaps with confirmed [c_start, c_end) iff t_val < c_end and slot_end_val > c_start
            is_booked = any(
                (t_val < c_end and slot_end_val > c_start)
                for c_start, c_end in confirmed_intervals
            )
            is_past = (target_date == today_in_aden and t_val <= now_in_aden.time())
            is_available = (not is_booked) and (not is_past)

            slots.append({
                'time': t_val.strftime('%H:%M:%S'),
                'time_formatted': format_time_arabic(t_val),
                'shift': shift_name,
                'shift_label': shift_label,
                'is_available': is_available,
                'is_booked': is_booked,
                'is_past': is_past,
            })
            current_dt += slot_delta

    # Morning Shift
    if working_hour.morning_start and working_hour.morning_end:
        generate_shift_slots(working_hour.morning_start, working_hour.morning_end, 'morning', _('الفترة الصباحية'))

    # Evening Shift
    if working_hour.evening_start and working_hour.evening_end:
        generate_shift_slots(working_hour.evening_start, working_hour.evening_end, 'evening', _('الفترة المسائية'))

    if not slots:
        return {
            'is_open': False,
            'reason': _('لا توجد فترات عمل محددة لهذا اليوم'),
            'slots': []
        }

    return {
        'is_open': True,
        'reason': '',
        'slots': slots,
    }


def create_appointment_request(full_name: str, phone_number: str, branch: ClinicBranch, appointment_date: date, appointment_time: time, email: str = '', service=None, visit_reason: str = '', patient_notes: str = '') -> Appointment:
    """
    Creates a pending patient appointment request safely with transactional integrity and strict server-side validation.
    """
    clean_phone = phone_number.strip()
    clean_name = full_name.strip()

    if not clean_phone or not clean_name:
        raise ValidationError(_('الاسم ورقم الهاتف مطلوبان.'))

    now_in_aden = datetime.now(ADEN_TZ)
    today_in_aden = now_in_aden.date()

    # 1. Past date / time check
    if appointment_date < today_in_aden:
        raise ValidationError(_('لا يمكن حجز موعد في تاريخ ماضٍ.'))
    if appointment_date == today_in_aden and appointment_time <= now_in_aden.time():
        raise ValidationError(_('لا يمكن حجز موعد في وقت انقضى بالفعل اليوم.'))

    # 2. Branch active check
    if not branch.is_active:
        raise ValidationError(_('فرع العيادة المحدد غير متاح لاستقبال الحجوزات حالياً.'))

    # 3. Holiday check
    holiday = ClinicHoliday.objects.filter(
        date=appointment_date
    ).filter(
        models.Q(branch=branch) | models.Q(branch__isnull=True)
    ).first()
    if holiday:
        raise ValidationError(f"{_('العيادة في عطلة رسمية في هذا التاريخ:')} {holiday.reason_ar}")

    # 4. Working hours and slot check
    model_day = get_model_day_of_week(appointment_date)
    working_hour = WorkingHours.objects.filter(branch=branch, day_of_week=model_day).first()
    if not working_hour or working_hour.is_closed:
        raise ValidationError(_('العيادة مغلقة في هذا اليوم المحدد (عطلة أسبوعية).'))

    # 5. Check if appointment_time falls within working shifts
    in_morning = (
        working_hour.morning_start and working_hour.morning_end and
        working_hour.morning_start <= appointment_time < working_hour.morning_end
    )
    in_evening = (
        working_hour.evening_start and working_hour.evening_end and
        working_hour.evening_start <= appointment_time < working_hour.evening_end
    )
    if not (in_morning or in_evening):
        raise ValidationError(_('الوقت المحدد يقع خارج ساعات العمل المعتمدة للعيادة.'))

    # Calculate end time of requested appointment slot
    req_duration = working_hour.slot_duration_minutes if working_hour else 20
    req_end_dt = datetime.combine(appointment_date, appointment_time) + timedelta(minutes=req_duration)
    req_end_time = req_end_dt.time()

    # 6. Check if requested slot interval overlaps with ANY already confirmed appointment on this branch
    conflict = Appointment.objects.filter(
        branch=branch,
        appointment_date=appointment_date,
        status=Appointment.Status.CONFIRMED,
        appointment_time__lt=req_end_time,
        end_time__gt=appointment_time
    ).exists()
    if conflict:
        raise ValidationError(_('هذا الموعد أو جزء من فترته الزمنية محجوز ومؤكد بالفعل لمريض آخر. يرجى اختيار موعد آخر.'))

    with transaction.atomic():
        # Get or create patient record
        patient, created = Patient.objects.get_or_create(
            phone_number=clean_phone,
            defaults={'full_name': clean_name, 'email': email.strip() or None}
        )
        if patient.full_name != clean_name:
            patient.full_name = clean_name
            if email and not patient.email:
                patient.email = email.strip()
            patient.save(update_fields=['full_name', 'email'])

        appointment = Appointment.objects.create(
            patient=patient,
            branch=branch,
            service=service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            duration_minutes=req_duration,
            end_time=req_end_time,
            visit_reason=visit_reason.strip(),
            patient_notes=patient_notes.strip(),
            status=Appointment.Status.PENDING
        )

        AppointmentStatusHistory.objects.create(
            appointment=appointment,
            old_status='',
            new_status=Appointment.Status.PENDING,
            notes=_('طلب حجز جديد مسجل عبر الموقع الإلكتروني')
        )

        return appointment


def update_appointment_status_safe(appointment_id: int, new_status: str, staff_user=None, notes: str = '') -> Appointment:
    """
    Safely transitions appointment status with row-level locking and PostgreSQL constraint protection
    to prevent overlapping appointment intervals and double bookings under concurrent multi-worker loads.
    """
    from django.db import IntegrityError
    try:
        with transaction.atomic():
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)
            old_status = appointment.status

            if new_status == Appointment.Status.CONFIRMED:
                # Calculate appointment interval
                apt_start = appointment.appointment_time
                apt_end = appointment.end_time
                if not apt_end:
                    apt_end_dt = datetime.combine(appointment.appointment_date, apt_start) + timedelta(minutes=appointment.duration_minutes)
                    apt_end = apt_end_dt.time()
                    appointment.end_time = apt_end

                # Interval overlap check: S1 < E2 and E1 > S2
                conflict = Appointment.objects.filter(
                    branch=appointment.branch,
                    appointment_date=appointment.appointment_date,
                    status=Appointment.Status.CONFIRMED,
                    appointment_time__lt=apt_end,
                    end_time__gt=apt_start
                ).exclude(id=appointment.id).exists()

                if conflict:
                    raise ValidationError(_('تعذر التأكيد: يوجد موعد آخر مؤكد مسبقاً يتعارض مع هذه الفترة الزمنية في نفس الفرع!'))

            appointment.status = new_status
            if notes:
                appointment.staff_notes = (appointment.staff_notes + f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {notes}").strip()
            appointment.save()

            AppointmentStatusHistory.objects.create(
                appointment=appointment,
                old_status=old_status,
                new_status=new_status,
                changed_by=staff_user,
                notes=notes or f"تغيير الحالة إلى {appointment.get_status_display()}"
            )

            return appointment
    except IntegrityError:
        raise ValidationError(_('تعذر التأكيد: يوجد موعد آخر مؤكد مسبقاً يتعارض مع هذه الفترة الزمنية في نفس الفرع!'))
