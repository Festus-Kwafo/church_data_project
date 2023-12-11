import logging

from django import forms
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField

from .models import User


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Username', min_length=4, max_length=50)
    branch_name = forms.CharField(label='Branch name', min_length=4, max_length=50)
    email = forms.EmailField(label='Email Address', max_length=100)
    phonenumber = forms.CharField(label='Phone Number', max_length=15)
    country = CountryField(blank_label="(Select country)").formfield()
    planted_on = forms.DateField(label='Planted on', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'branch_name', 'phonenumber', 'country', 'planted_on')
        widgets = {"country": CountrySelectWidget()}

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise forms.ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            logging.debug(f"{email} Email already exists")
            raise forms.ValidationError(
                'Please use another Email, that is already taken')
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'OyibiAdmin'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'johndoe@gmail.com', 'name': 'email', 'id': 'id_email'})
        self.fields['branch_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Oyibi', 'name': 'branch_name', 'id': 'id_branch'})
        self.fields['phonenumber'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': '0555358099'})


class SendOTPForms(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phonenumber',)

class NewPasswordForm(forms.Form):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)


