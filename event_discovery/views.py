from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core.models import Event
from .models import Bookmark


def event_list(request):

    events = Event.objects.filter(
        event_approval_status='Approved'
    )

    search = request.GET.get('search')
    category = request.GET.get('category')
    skill = request.GET.get('skill')
    date = request.GET.get('date')

    if search:
        events = events.filter(
            event_title__icontains=search
        )

    if category:
        events = events.filter(
            event_category__icontains=category
        )

    if skill:
        events = events.filter(
            skill_tags__icontains=skill
        )

    if date:
        events = events.filter(
            event_date=date
        )

    return render(request, 'event_list.html', {
        'events': events.order_by('event_date')
    })


def event_detail(request, event_id):

    event = get_object_or_404(
        Event,
        id=event_id
    )

    return render(request, 'event_detail.html', {
        'event': event
    })


@login_required
def save_event(request, event_id):

    event = get_object_or_404(
        Event,
        id=event_id
    )

    Bookmark.objects.get_or_create(
        user=request.user,
        event=event
    )

    return redirect('saved_events')


@login_required
def saved_events(request):

    view_mode = request.GET.get('view', 'card')

    bookmarks = Bookmark.objects.filter(
        user=request.user
    ).select_related('event')

    return render(request, 'saved_events.html', {
        'bookmarks': bookmarks,
        'view_mode': view_mode
    })


@login_required
def delete_saved_event(request, bookmark_id):

    bookmark = get_object_or_404(
        Bookmark,
        id=bookmark_id,
        user=request.user
    )

    bookmark.delete()

    return redirect('saved_events')