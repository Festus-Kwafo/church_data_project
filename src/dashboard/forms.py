from django import forms
from .models import Attendance
from django.core.exceptions import ValidationError


class AtttendanceForms(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude = ["branch", "approved", "total"]

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        if Attendance.objects.filter(date=date).exists():
            raise ValidationError('This date already exists in the database.')
