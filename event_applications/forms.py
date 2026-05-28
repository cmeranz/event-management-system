from django import forms
from core.models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['application_statement']

        widgets = {
            'application_statement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Briefly tell the organizer why you want to join this event. This is optional.'
            }),
        }

        labels = {
            'application_statement': 'Application Statement'
        }