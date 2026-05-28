from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from accounts.decorators import organizer_required
from django.db.models import Count, Q
from core.models import Event, Application
from .forms import EventForm
from django.contrib import messages

POINTS_BY_CATEGORY = {
    'Workshop': 50,
    'Seminar': 20,
    'Volunteer': 100,
    'Competition': 150,
}

@organizer_required
@never_cache
def organizer_dashboard(request):
    my_events = Event.objects.filter(event_organizer=request.user)

    my_applications = Application.objects.filter(
        Q(application_event__event_organizer=request.user) |
        Q(event_ID__event_organizer=request.user)
    ).distinct()

    recent_events = my_events.order_by('-event_created_at')[:5]
    recent_applications = my_applications.select_related(
        'application_applicant',
        'application_event',
        'event_ID'
    ).order_by('-application_applied_on')[:5]

    context = {
        'total_events': my_events.count(),
        'pending_events': my_events.filter(event_approval_status='Pending').count(),
        'approved_events': my_events.filter(event_approval_status='Approved').count(),
        'rejected_events': my_events.filter(event_approval_status='Rejected').count(),
        'total_applications': my_applications.count(),
        'pending_applications': my_applications.filter(application_status='Pending').count(),
        'approved_applications': my_applications.filter(application_status='Approved').count(),
        'recent_events': recent_events,
        'recent_applications': recent_applications,
    }

    return render(request, 'organizer/dashboard.html', context)


@organizer_required
@never_cache
def organizer_events(request):
    events = Event.objects.filter(event_organizer=request.user).order_by('-event_date')
    return render(request, 'organizer/events.html', {'events': events})


@organizer_required
@never_cache
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)
            event.event_organizer = request.user
            event.event_approval_status = 'Pending'
            event.points_awarded = POINTS_BY_CATEGORY.get(event.event_category, 0)
            event.save()
            return redirect('organizer:events')
    else:
        form = EventForm()

    return render(request, 'organizer/event_form.html', {
        'form': form,
        'title': 'Create Event',
        'button_text': 'Create Event'
    })

@organizer_required
@never_cache
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, event_organizer=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            updated_event = form.save(commit=False)
            updated_event.event_approval_status = 'Pending'
            updated_event.points_awarded = POINTS_BY_CATEGORY.get(updated_event.event_category, 0)
            updated_event.save()
            return redirect('organizer:events')
    else:
        form = EventForm(instance=event)

    return render(request, 'organizer/event_form.html', {
        'form': form,
        'title': 'Edit Event',
        'button_text': 'Save Changes'
    })


@organizer_required
@never_cache
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, event_organizer=request.user)

    if request.method == 'POST':
        event.delete()
        return redirect('organizer:events')

    return render(request, 'organizer/confirm_delete.html', {'event': event})


@organizer_required
@never_cache
def event_applicants(request, event_id):
    event = get_object_or_404(Event, id=event_id, event_organizer=request.user)

    applications = Application.objects.filter(
        Q(application_event=event) | Q(event_ID=event)
    ).select_related('application_applicant').distinct().order_by('-application_applied_on')

    return render(request, 'organizer/event_applicants.html', {
        'event': event,
        'applications': applications,
    })

@organizer_required
@never_cache
def update_applicant_status(request, application_id, status):
    application = get_object_or_404(
        Application,
        id=application_id
    )

    event = application.application_event or application.event_ID

    if event.event_organizer != request.user:
        return redirect('organizer:events')

    if request.method == 'POST' and status in ['Approved', 'Rejected']:
        application.application_status = status
        application.save()

    return redirect('organizer:event_applicants', event_id=event.id)

@organizer_required
@never_cache
def update_attendance(request, application_id, attendance_status):
    application = get_object_or_404(
        Application,
        id=application_id
    )

    event = application.application_event or application.event_ID

    if not event:
        messages.error(request, 'This application is not linked to a valid event.')
        return redirect('organizer:events')

    if event.event_organizer != request.user:
        messages.error(request, 'You can only mark attendance for your own events.')
        return redirect('organizer:events')

    if application.application_status != 'Approved':
        messages.error(request, 'Only approved applicants can be marked as attended.')
        return redirect('organizer:event_applicants', event_id=event.id)

    if attendance_status == 'attended':
        application.attended = True
        application.save()
        messages.success(
            request,
            f'{application.application_applicant.get_full_name() or application.application_applicant.username} has been marked as attended.'
        )

    elif attendance_status == 'not_attended':
        application.attended = False
        application.save()
        messages.info(
            request,
            f'Attendance has been removed for {application.application_applicant.get_full_name() or application.application_applicant.username}.'
        )

    else:
        messages.error(request, 'Invalid attendance action.')

    return redirect('organizer:event_applicants', event_id=event.id)