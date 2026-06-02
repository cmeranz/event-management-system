from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import student_required
from core.models import Event, Application
from .forms import ApplicationForm


@student_required
def apply_event(request, event_id):
    event = get_object_or_404(
        Event,
        id=event_id,
        event_approval_status='Approved'
    )

    existing_application = Application.objects.filter(
        application_applicant=request.user
    ).filter(
        application_event=event
    ).first()

    if not existing_application:
        existing_application = Application.objects.filter(
            application_applicant=request.user,
            event_ID=event
        ).first()

    if existing_application:
        messages.info(request, 'You have already applied for this event.')
        return redirect('event_discovery:event_detail', event_id=event.id)

    approved_count = Application.objects.filter(
        Q(application_event=event) | Q(event_ID=event),
        application_status='Approved'
    ).count()

    if event.event_capacity and approved_count >= event.event_capacity:
        messages.error(request, 'This event has reached its capacity.')
        return redirect('event_discovery:event_detail', event_id=event.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)

        if form.is_valid():
            application = form.save(commit=False)
            application.application_event = event
            application.event_ID = event
            application.application_applicant = request.user
            application.application_status = 'Pending'
            application.save()

            messages.success(request, 'Your application has been submitted successfully. Your status is now pending.')
            return redirect('event_discovery:event_detail', event_id=event.id)
    else:
        form = ApplicationForm()

    return render(request, 'event_applications/apply_event.html', {
        'form': form,
        'event': event
    })

@student_required
def cancel_application(request, application_id):
    application = get_object_or_404(
        Application,
        id=application_id,
        application_applicant=request.user
    )

    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Your application has been cancelled.')
        return redirect('accounts:profile')
    
    # For GET requests, redirect to profile
    return redirect('accounts:profile')


   

@student_required
def my_applications(request):
    status_filter = request.GET.get('status', '').strip()
    category_filter = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    applications = Application.objects.filter(
        application_applicant=request.user
    ).select_related(
        'application_event',
        'event_ID'
    ).order_by('-application_applied_on')

    if status_filter == 'Pending':
        applications = applications.filter(application_status='Pending')

    elif status_filter == 'Approved':
        applications = applications.filter(application_status='Approved', attended=False)

    elif status_filter == 'Rejected':
        applications = applications.filter(application_status='Rejected')

    elif status_filter == 'Attended':
        applications = applications.filter(attended=True)

    if category_filter:
        applications = applications.filter(
            Q(application_event__event_category__iexact=category_filter) |
            Q(event_ID__event_category__iexact=category_filter)
        )

    if search_query:
        applications = applications.filter(
            Q(application_event__event_title__icontains=search_query) |
            Q(event_ID__event_title__icontains=search_query)
        )

    categories = ['Workshop', 'Seminar', 'Volunteer', 'Competition']

    context = {
        'applications': applications,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': categories,
        'total_applications': applications.count(),
    }

    return render(request, 'event_applications/my_applications.html', context)