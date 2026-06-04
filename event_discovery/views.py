from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from core.models import Event, Application
from django.views.decorators.http import require_POST
from accounts.decorators import student_required
from .models import SavedEvent
from django.contrib import messages

EVENT_CATEGORIES = [
    'Workshop',
    'Seminar',
    'Volunteer',
    'Competition',
]


def attach_application_status(request, events):
    events = list(events)

    for event in events:
        event.user_application_status = None
        event.is_saved = False

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role == 'Student':
            applications = Application.objects.filter(
                application_applicant=request.user
            ).select_related('application_event', 'event_ID')

            status_by_event_id = {}

            for app in applications:
                if app.application_event:
                    status_by_event_id[app.application_event.id] = app.application_status
                if app.event_ID:
                    status_by_event_id[app.event_ID.id] = app.application_status

            saved_event_ids = set(
                SavedEvent.objects.filter(student=request.user)
                .values_list('event_id', flat=True)
            )

            for event in events:
                event.user_application_status = status_by_event_id.get(event.id)
                event.is_saved = event.id in saved_event_ids

    return events


def home(request):
    featured_events = Event.objects.filter(
        event_approval_status='Approved'
    ).order_by('event_date')[:3]

    featured_events = attach_application_status(request, featured_events)

    context = {
        'featured_events': featured_events,
    }

    return render(request, 'event_discovery/home.html', context)


def event_list(request):
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    skill_filter = request.GET.get('skill', '').strip()

    events = Event.objects.filter(
        event_approval_status='Approved'
    ).order_by('event_date')

    if search_query:
        events = events.filter(
            Q(event_title__icontains=search_query) |
            Q(event_description__icontains=search_query) |
            Q(event_location__icontains=search_query)
        )

    if category_filter:
        events = events.filter(event_category__iexact=category_filter)

    if skill_filter:
        events = events.filter(skill_tags__icontains=skill_filter)

    events = attach_application_status(request, events)

    context = {
        'events': events,
        'categories': EVENT_CATEGORIES,
        'search_query': search_query,
        'category_filter': category_filter,
        'skill_filter': skill_filter,
    }

    return render(request, 'event_discovery/event_list.html', context)


def event_detail(request, event_id):
    event = get_object_or_404(
        Event,
        id=event_id,
        event_approval_status='Approved'
    )

    event.user_application_status = None
    event.is_saved = False

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role == 'Student':
            application = Application.objects.filter(
                application_applicant=request.user
            ).filter(
                Q(application_event=event) | Q(event_ID=event)
            ).first()

            if application:
                event.user_application_status = application.application_status
                event.user_application_id = application.id
            else:
                event.user_application_id = None

            event.is_saved = SavedEvent.objects.filter(
                student=request.user,
                event=event
            ).exists()

    return render(request, 'event_discovery/event_detail.html', {
        'event': event
    })


@student_required
@require_POST
def toggle_saved_event(request, event_id):
    event = get_object_or_404(
        Event,
        id=event_id,
        event_approval_status='Approved'
    )

    saved_event, created = SavedEvent.objects.get_or_create(
        student=request.user,
        event=event
    )

    if created:
        messages.success(request, f'"{event.event_title}" has been saved to your events.')
    else:
        saved_event.delete()
        messages.info(request, f'"{event.event_title}" has been removed from your saved events.')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'event_discovery:event_list'
    return redirect(next_url)

def contact(request):
    return render(request, 'event_discovery/contact.html')