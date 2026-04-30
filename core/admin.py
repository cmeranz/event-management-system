from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Event, Application


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # This controls which columns show up in the admin list
    list_display = ('event_title', 'event_organizer', 'event_approval_status', 'event_date', 'event_capacity')

    # This adds a filter sidebar on the right
    list_filter = ('event_approval_status', 'event_date')

    # This adds a search bar at the top
    search_fields = ('event_title', 'event_description')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_applicant', 'application_event', 'application_status', 'attended')
    list_filter = ('application_status', 'attended')
    search_fields = ('application_applicant__username', 'application_event__event_title')