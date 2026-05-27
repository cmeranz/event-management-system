from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('saved/', views.saved_events, name='saved_events'),
    path('bookmark/<int:event_id>/', views.save_event, name='save_event'),
    path('delete-bookmark/<int:bookmark_id>/',views.delete_saved_event,name='delete_saved_event'),
]