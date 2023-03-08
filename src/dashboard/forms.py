from django import forms
from .models import Attendance

class AtttendanceForms(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude = ["branch", "approved", "total"]