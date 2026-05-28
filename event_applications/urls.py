from django.urls import path
from . import views

app_name = 'event_applications'

urlpatterns = [
    path('apply/<int:event_id>/', views.apply_event, name='apply_event'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('cancel/<int:application_id>/', views.cancel_application, name='cancel_application'),
]