from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .decorators import student_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm, ProfileForm, StyledPasswordResetForm, StyledSetPasswordForm
from .models import UserProfile
from django.db.models import Q
from core.models import Application
from event_discovery.models import SavedEvent


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:redirect_dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            student_staff_id = form.cleaned_data.get('student_staff_id')
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            password = form.cleaned_data['password1']

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            UserProfile.objects.create(
                user=user,
                student_staff_id=student_staff_id,
                role=role
            )

            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:redirect_dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:redirect_dashboard')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
@never_cache
def logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    response = redirect('accounts:login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
@never_cache
@login_required
@never_cache
def redirect_dashboard(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('admin_dashboard')

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'Student',
            'student_staff_id': ''
        }
    )

    if profile.role == 'Organizer':
        return redirect('organizer:dashboard')

    return redirect('event_discovery:home')


@student_required
@never_cache
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')


@login_required
@never_cache
def profile_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'Student',
            'student_staff_id': ''
        }
    )

    applications = Application.objects.filter(
        application_applicant=request.user
    ).select_related(
        'application_event',
        'event_ID'
    ).order_by('-application_applied_on')

    total_applications = applications.count()
    pending_applications = applications.filter(application_status='Pending').count()
    approved_applications = applications.filter(application_status='Approved').count()
    rejected_applications = applications.filter(application_status='Rejected').count()
    attended_applications = applications.filter(attended=True)

    total_points = 0
    gained_skills = set()

    for app in attended_applications:
        event = app.application_event or app.event_ID

        if event:
            total_points += event.points_awarded or 0

            for skill in event.skill_list:
                gained_skills.add(skill)

    attended_count = attended_applications.count()
    gained_skills = sorted(gained_skills)

    milestones = [
    {'title': 'Aspiring Explorer', 'points': 0, 'icon': 'bi-compass'},
    {'title': 'Active Participant', 'points': 100, 'icon': 'bi-lightning-charge'},
    {'title': 'Skill Seeker', 'points': 300, 'icon': 'bi-stars'},
    {'title': 'Event Enthusiast', 'points': 700, 'icon': 'bi-calendar-event'},
    {'title': 'Master Contributor', 'points': 1500, 'icon': 'bi-trophy'},
    ]

    current_milestone = milestones[0]
    next_milestone = None

    for milestone in milestones:
        if total_points >= milestone['points']:
            current_milestone = milestone
        elif total_points < milestone['points'] and next_milestone is None:
            next_milestone = milestone

    if next_milestone:
        points_needed = next_milestone['points'] - total_points
        progress_percent = int((total_points / next_milestone['points']) * 100)
    else:
        points_needed = 0
        progress_percent = 100

    saved_events = SavedEvent.objects.filter(
    student=request.user,
    event__event_approval_status='Approved'
    ).select_related('event')[:4]

    saved_events_count = SavedEvent.objects.filter(
        student=request.user,
        event__event_approval_status='Approved'
    ).count()

    context = {
        'profile': profile,
        'applications': applications[:5],
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'rejected_applications': rejected_applications,
        'attended_count': attended_count,
        'total_points': total_points,
        'gained_skills': gained_skills,
        'milestones': milestones,
        'current_milestone': current_milestone,
        'next_milestone': next_milestone,
        'points_needed': points_needed,
        'progress_percent': progress_percent,
        'saved_events': saved_events,
        'saved_events_count': saved_events_count,
    }

    return render(request, 'accounts/profile.html', context)

@login_required
@never_cache
def edit_profile_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'Student',
            'student_staff_id': ''
        }
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)

        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.username = form.cleaned_data['email']
            request.user.save()

            form.save()

            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(
            instance=profile,
            user=request.user,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'student_staff_id': profile.student_staff_id,
            }
        )

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'profile': profile
    })

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    form_class = StyledPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    form_class = StyledSetPasswordForm