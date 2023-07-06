from django import forms
from django.core.exceptions import ValidationError

from .models import Attendance, SundayAttendance, WednesdayAttendance


class SundayAttendanceForms(forms.ModelForm):
    class Meta:
        model = SundayAttendance
        exclude = ["attendance", "branch_name", "approved", "total", "leaders_to_members", "leaders_to_offering", "members_to_offering"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs.update({'type': 'date'})

class AttendanceForms(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude = ["branch", "total"]

class WednesdayAttendanceForms(forms.ModelForm):
    class Meta:
        model = WednesdayAttendance
        exclude = ["attendance", "branch_name", "approved"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'type': 'date'})
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'