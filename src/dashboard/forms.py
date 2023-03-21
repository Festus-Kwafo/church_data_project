from django import forms
from .models import Attendance
from django.core.exceptions import ValidationError


class AtttendanceForms(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude = ["branch", "approved", "total"]