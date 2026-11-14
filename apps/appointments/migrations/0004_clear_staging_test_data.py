from django.db import migrations


def clear_staging_appointments(apps, schema_editor):
    """Delete all staging test appointment and patient data."""
    AppointmentStatusHistory = apps.get_model('appointments', 'AppointmentStatusHistory')
    Appointment = apps.get_model('appointments', 'Appointment')
    Patient = apps.get_model('appointments', 'Patient')

    # Only delete test data with the known staging phone pattern
    staging_phones = [
        '+967 770 000 001',
        '+967 770 000 002',
        '+967 770 000 003',
        '+967 770 000 004',
    ]

    staging_patients = Patient.objects.filter(phone_number__in=staging_phones)
    staging_apt_ids = Appointment.objects.filter(patient__in=staging_patients).values_list('id', flat=True)

    AppointmentStatusHistory.objects.filter(appointment_id__in=staging_apt_ids).delete()
    Appointment.objects.filter(id__in=staging_apt_ids).delete()
    staging_patients.delete()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_appointment_duration_minutes_appointment_end_time_and_more'),
    ]

    operations = [
        migrations.RunPython(clear_staging_appointments, backwards),
    ]
