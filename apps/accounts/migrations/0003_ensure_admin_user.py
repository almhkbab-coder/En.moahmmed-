from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_or_update_admin(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    password_hash = make_password('admin123!')

    user = CustomUser.objects.filter(username='admin').first()
    if not user:
        user = CustomUser.objects.filter(username='admin_staging').first()

    if user:
        user.username = 'admin'
        user.password = password_hash
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'super_admin'
        user.save()
    else:
        CustomUser.objects.create(
            username='admin',
            email='admin@staging.alsayyad-clinic.ye',
            password=password_hash,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            role='super_admin'
        )


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_profile_image'),
    ]

    operations = [
        migrations.RunPython(create_or_update_admin, backwards),
    ]
