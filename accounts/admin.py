from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_staff_id', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'student_staff_id')