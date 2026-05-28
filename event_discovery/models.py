from django.db import models
from django.contrib.auth.models import User
from core.models import Event


class SavedEvent(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='saved_by_students')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'event')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.student.username} saved {self.event.event_title}"