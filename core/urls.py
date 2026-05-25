from django.urls import path
from . import views

urlpatterns = [
    path('admin-applications/', views.admin_applications, name='admin_applications'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-events/', views.admin_events, name='admin_events'),
#path('approve-events/', views.event_approval_list, name='admin_events'),
    path('update-status/<int:event_id>/', views.update_event_status, name='update_event_status'),
    path('update-status/<int:pk>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('export-applications/', views.export_applications_csv, name='export_applications_csv'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('save-event/<int:event_id>/', views.save_event, name='save_event'),
    path('events/saved/', views.saved_events, name='saved_events'),
]
