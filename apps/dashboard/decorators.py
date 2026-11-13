from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.accounts.models import CustomUser


def role_required(allowed_roles):
    """
    Decorator enforcing role-based access control (RBAC).
    Superusers automatically bypass restrictions.
    Raises PermissionDenied (HTTP 403) if the user's role is not authorized.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('dashboard:login')
            if request.user.is_superuser or request.user.role == CustomUser.Role.SUPER_ADMIN:
                return view_func(request, *args, **kwargs)
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied(_("عذراً، ليس لديك الصلاحية الكافية للوصول إلى هذه الصفحة أو تنفيذ هذه العملية."))
        return _wrapped_view
    return decorator


def super_admin_only(view_func):
    """Strictly for Super Administrator role"""
    return role_required([CustomUser.Role.SUPER_ADMIN])(view_func)


def doctor_or_admin_required(view_func):
    """For Doctor and Super Administrator roles"""
    return role_required([CustomUser.Role.SUPER_ADMIN, CustomUser.Role.DOCTOR])(view_func)


def appointment_staff_required(view_func):
    """For Receptionists, Doctors, and Super Administrators"""
    return role_required([CustomUser.Role.SUPER_ADMIN, CustomUser.Role.DOCTOR, CustomUser.Role.RECEPTIONIST])(view_func)


def content_staff_required(view_func):
    """For Content Managers, Doctors, and Super Administrators"""
    return role_required([CustomUser.Role.SUPER_ADMIN, CustomUser.Role.DOCTOR, CustomUser.Role.CONTENT_MANAGER])(view_func)

