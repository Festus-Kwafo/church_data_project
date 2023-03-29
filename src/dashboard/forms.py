from django import forms
from .models import Attendance
from django.core.exceptions import ValidationError


class AtttendanceForms(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude = ["branch", "approved", "total", "leaders_to_members", "leaders_to_offering", "members_to_offering"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs.update({'type': 'date'})
