import datetime
from datetime import time, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
from .models import Event, Application

# --- General Navigation ---

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# --- Event Management Module ---

def admin_events(request):
    # Fetch all events and send to the template
    all_events = Event.objects.all().order_by('-event_date')
    return render(request, 'admin_events.html', {'events': all_events})

def update_event_status(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        new_status = request.POST.get('status')
        if new_status:
            event.event_approval_status = new_status
            event.save()
    return redirect('admin_events')

# --- Applications Module (Filters & Stats) ---

def admin_applications(request):
    # 1. Setup basic time variables for KL
    today_date = timezone.now().date()

    # 2. Get filter values from the URL (GET parameters)
    search_query = request.GET.get('search', '')
    event_filter = request.GET.get('event', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date_filter', '')

    # 3. Start with all applications
    applications = Application.objects.all().select_related('application_applicant', 'event_ID')

    local_now = timezone.now()
    start_of_day = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = local_now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # 4. Apply Filters Dynamically to the QuerySet
    if search_query:
        applications = applications.filter(
            Q(application_applicant__username__icontains=search_query) |
            Q(application_applicant__email__icontains=search_query) |
            Q(application_applicant__first_name__icontains=search_query)
        )

    if event_filter:
        applications = applications.filter(event_ID_id=event_filter)

    if status_filter:
        applications = applications.filter(application_status=status_filter)

    if date_filter == 'today':
        # 1. Get the current time in KL
        now = timezone.now()

        # 2. Create a "Start of Day" (00:00:00) and "End of Day" (23:59:59)
        # This ensures the filter covers the full 24 hours of May 1st in KL
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # 3. Filter between these two specific moments
        applications = applications.filter(application_applied_on__range=(start_of_day, end_of_day))

    elif date_filter == 'week':
        last_week = today_date - timedelta(days=7)
        applications = applications.filter(application_applied_on__date__gte=last_week)

    # 5. Build Context with Stats and Filtered List
    context = {
        'applications': applications.order_by('-application_applied_on'),
        'events': Event.objects.all(),
        'total_count': Application.objects.count(),
        'pending_count': Application.objects.filter(application_status='Pending').count(),
        'approved_today_count': Application.objects.filter(
            application_status='Approved',
            application_applied_on__range=(start_of_day, end_of_day)
        ).count(),
    }
    return render(request, 'admin_applications.html', context)

# --- Application Logic ---

def update_application_status(request, pk, status):
    if request.method == 'POST':
        application = get_object_or_404(Application, pk=pk)
        application.application_status = status
        application.save()
    return redirect('admin_applications')


import csv
from django.http import HttpResponse
from django.utils import timezone  # Import this!


def export_applications_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="event_applications_KL.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Email', 'Event Title', 'Date Applied', 'Time Applied', 'Status'])

    applications = Application.objects.all().select_related('application_applicant', 'event_ID')

    for app in applications:
        # Convert the UTC time from the database to your local KL time
        local_time = timezone.localtime(app.application_applied_on)

        writer.writerow([
            app.application_applicant.get_full_name() or app.application_applicant.username,
            app.application_applicant.email,
            app.event_ID.event_title,
            local_time.strftime('%Y-%m-%d'),  # Date in KL
            local_time.strftime('%I:%M %p'),  # Time in KL (12-hour format)
            app.application_status
        ])

    return response


#--------------Admin Dashboard------
# --- Admin Dashboard ---
from django.db.models import Count


def admin_dashboard(request):
    # 1. Application Status Data (Doughnut Chart)
    status_counts = Application.objects.values('application_status').annotate(total=Count('id'))

    # 2. Event Capacity Data (Bar Chart)
    # We need to fetch the title, the max capacity, and count the approved applications
    events = Event.objects.annotate(
        total_apps=Count('application'),
        # Count only applications where status is 'Approved'
        approved_apps=Count('application', filter=Q(application__application_status='Approved'))
    )[:5]  # Limit to top 5 so the chart isn't crowded

    context = {
        # Data for the Doughnut Chart
        'chart_labels': [item['application_status'] for item in status_counts],
        'chart_data': [item['total'] for item in status_counts],

        # Data for the Bar Chart
        'event_labels': [e.event_title for e in events],
        'approved_data': [e.approved_apps for e in events],
        'total_app_data': [e.total_apps for e in events],
    }
    return render(request, 'admin_dashboard.html', context)