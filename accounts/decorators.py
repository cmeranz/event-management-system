from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test


def is_student(user):
    return (
        user.is_authenticated
        and not user.is_staff
        and not user.is_superuser
        and hasattr(user, 'profile')
        and user.profile.role == 'Student'
    )


def is_organizer(user):
    return (
        user.is_authenticated
        and not user.is_staff
        and not user.is_superuser
        and hasattr(user, 'profile')
        and user.profile.role == 'Organizer'
    )


def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


student_required = user_passes_test(is_student, login_url='accounts:login')
organizer_required = user_passes_test(is_organizer, login_url='accounts:login')
admin_required = user_passes_test(is_admin_user, login_url='accounts:login')