from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Organizer', 'Organizer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    student_staff_id = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    interests = models.ManyToManyField('core.InterestTag', blank=True, related_name='interested_profiles')
    skills = models.ManyToManyField('core.SkillTag', blank=True, related_name='skilled_profiles')

    def __str__(self):
        return f"{self.user.username} - {self.role}"