from django import forms
from core.models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'event_title',
            'event_description',
            'event_date',
            'event_location',
            'event_image',
            'points_awarded',
            'skill_tags',
            'event_capacity',
            'event_category',
        ]

        widgets = {
            'event_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Python Workshop'
            }),
            'event_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the event, activities, and target participants.'
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'event_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Faculty of Computer Science'
            }),
            'event_image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'points_awarded': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'skill_tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Python, Teamwork, Communication'
            }),
            'event_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 60
            }),
            'event_category': forms.Select(
                choices=[
                    ('Workshop', 'Workshop'),
                    ('Seminar', 'Seminar'),
                    ('Volunteer', 'Volunteer'),
                    ('Competition', 'Competition'),
                ],
                attrs={'class': 'form-select'}
            ),
        }