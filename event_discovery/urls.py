from django.urls import path
from . import views

app_name = 'event_discovery'

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/save/', views.toggle_saved_event, name='toggle_saved_event'),
    path('contact/', views.contact, name='contact'),
]