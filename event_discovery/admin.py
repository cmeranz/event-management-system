from django.contrib import admin
from .models import SavedEvent


@admin.register(SavedEvent)
class SavedEventAdmin(admin.ModelAdmin):
    list_display = ('student', 'event', 'saved_at')
    search_fields = ('student__username', 'student__email', 'event__event_title')
    list_filter = ('saved_at',)