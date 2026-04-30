

from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    # Approval status options
    APPROVAL_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # Organizer & Details
    event_organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    event_title = models.CharField(max_length=200)
    event_description = models.TextField()
    event_date = models.DateField()
    event_location = models.CharField(max_length=255)

    # Workflow Status
    event_approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='Pending'
    )
    event_created_at = models.DateTimeField(auto_now_add=True)

    # Files & Points
    # This will save files to /media/event_images/ on your local drive
    event_image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    points_awarded = models.IntegerField(default=0)
    skill_tags = models.CharField(max_length=255, help_text="List skills separated by commas")

    event_capacity = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of attendees allowed"
    )
    event_category = models.CharField(max_length=100, default='General')
    def __str__(self):
        return self.event_title


class Application(models.Model):
    # Application status options
    APP_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # Links
    application_event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='applications')
    application_applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_applications')
    event_ID = models.ForeignKey('Event', on_delete=models.CASCADE, null=True, blank=True)
    # Application Info
    application_status = models.CharField(
        max_length=20,
        choices=APP_STATUS_CHOICES,
        default='Pending'
    )
    application_statement = models.TextField(blank=True, null=True)
    application_applied_on = models.DateTimeField(auto_now_add=True)

    # Post-Event Attendance
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.application_applicant.username} - {self.application_event.event_title}"
