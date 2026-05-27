from django.contrib.auth.models import User
from django.db import models
from core.models import Event


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} saved {self.event.event_title}"