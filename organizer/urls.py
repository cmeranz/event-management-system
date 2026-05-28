from django.urls import path
from . import views

app_name = 'organizer'

urlpatterns = [
    path('dashboard/', views.organizer_dashboard, name='dashboard'),
    path('events/', views.organizer_events, name='events'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<int:event_id>/applicants/', views.event_applicants, name='event_applicants'),
    path(
    'applications/<int:application_id>/<str:status>/',
    views.update_applicant_status,
    name='update_applicant_status'
    ),
    path('applications/<int:application_id>/attendance/<str:attendance_status>/', views.update_attendance, name='update_attendance'),
]