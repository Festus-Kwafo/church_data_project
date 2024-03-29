import os
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from .models import User
from accounts.utils.functions import get_errors_from_form, send_otp_sms, get_otp, generate_password
from core.validators import CustomPasswordValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import logging


from .forms import RegistrationForm, SendOTPForms, NewPasswordForm, ChangePasswordForm

from dotenv import load_dotenv

load_dotenv()

class LoginView(View):
    template_name = 'templates/accounts/login.html'

    def get(self, request):
        logging.debug("Login page requested" + request.get_full_path())
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = "on" in request.POST.get("remember_me", "")
        logging.debug(f"Login attempt for {username} with remember_me={remember_me}")
        user = authenticate(username=username, password=password)

        if user and user.user_must_change_password:
            logging.debug(f"{username} User logged in with default password, redirecting to change password page")
            login(request, user)
            return redirect('accounts:change_password')  # Redirect to the change password page

        if user:
            logging.debug(f"{username} User logged in successfully")
            login(request, user)
            if remember_me:
                request.session.set_expiry(86400 * 30)
            user.last_login = timezone.now()
            user.save()
            redirect_url = request.GET.get("next") or "dashboard:index"
            return redirect(redirect_url)
        else:
            context = {k: v for k, v in request.POST.items()}
            logging.debug(f"{username} User login failed")
            messages.warning(request, "Invalid credentials")
            return render(request, self.template_name, context)


class RegisterBranch(View):
    template_name = 'templates/accounts/register.html'

    @method_decorator(staff_member_required)
    def get(self, request):
        registerForm = RegistrationForm(request.POST)
        context = {'forms': registerForm}
        logging.debug("Register page requested" + request.get_full_path())
        return render(self.request, self.template_name, context)

    def post(self, request):
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            logging.debug(f"Generate password for {user.username}")
            password = generate_password()
            send_otp_sms(password, user.phonenumber)
            user.set_password(password)
            user.created_at = timezone.now()
            user.save()
            logging.debug(f"{user.username} User registered successfully")
        else:
            error_message = get_errors_from_form(registerForm)
            messages.warning(request, error_message)
            logging.debug(f"User registration failed")
            return redirect('accounts:register')
        return redirect('accounts:login')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out")
        logging.debug(f"{request.user.username} User logged out successfully")
        return redirect('accounts:login')


class SendOTP(View):
    template_name = 'templates/accounts/reset_password.html'
    otp_number = get_otp()

    def get(self, request):
        form = SendOTPForms()
        logging.debug("Reset Password page requested" + request.get_full_path())
        return render(request, self.template_name, {'forms': form})

    def post(self, request):
        form = SendOTPForms(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phonenumber')
            user = User.objects.filter(phonenumber=phone_number)
            if user:
                otp_user = User.objects.get(phonenumber=phone_number)
                otp_user.otp_number = self.otp_number
                logging.debug(f"{otp_user.username} User requested for OTP {self.otp_number}")
                otp_user.otp_verified = False
                otp_user.save()
                send_otp_sms(self.otp_number, phone_number)
                logging.debug(f"{otp_user.username} User OTP sent successfully")
                request.session['session_number'] = f'{phone_number}'
                return redirect("accounts:otp_verification")
            else:
                logging.error(f"User does not exist with {phone_number}")
                messages.warning(request, "Account does not Exist with is PhoneNumber")
                return redirect("accounts:reset_password")
        else:
            messages.warning(request, get_errors_from_form(form))
        return redirect("accounts:reset_password")


class OTPVerification(View):
    template_name = 'templates/accounts/otp_verification.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        otp_number = request.POST.get('otp_number')
        phone_number = request.session.get('session_number')
        if User.objects.filter(phonenumber=phone_number, otp_number=otp_number).exists():
            user = User.objects.get(phonenumber=phone_number, otp_number=otp_number)
            user.otp_verified = True
            user.save()
            login(request, user)
            return redirect("accounts:new_password")
        else:
            messages.warning(request, "OTP does not match")
        return render(request, self.template_name)


def resend_otp(request):
    phone_number = request.session.get('session_number')
    user = User.objects.get(phonenumber=phone_number)
    user.otp_number = get_otp()
    logging.debug(f"{user.username} User requested for OTP {user.otp_number}")
    user.save()
    send_otp_sms(user.otp_number, phone_number)
    return redirect("accounts:otp_verification")


class NewPassword(View):
    def get(self, request):
        form = NewPasswordForm()
        logging.debug("New Password page requested" + request.get_full_path())
        return render(request, 'templates/accounts/new_password.html', {'forms': form})

    def post(self, request):
        form = NewPasswordForm(request.POST)
        # Validate the password
        validator = CustomPasswordValidator()
        if form.is_valid():
            password1 = form.cleaned_data.get('new_password1')
            password2 = form.cleaned_data.get('new_password2')
            try:
                validator.validate(password1)
                logging.debug(f"{request.user.username} User validation passed")
            except ValidationError as e:
                logging.debug(f"{request.user.username} User changed password failed")
                return JsonResponse({'status': 'error', 'message': str(e.message)})
            if password1 == password2:
                user = request.user
                user.set_password(password1)
                user.save()
                logging.debug(f"{request.user.username} User changed password successfully")
                update_session_auth_hash(request, user)
                logging.debug(f"{request.user.username} User logged out successfully")
                logout(request)
                return JsonResponse({'status': 'success', 'message': 'Password Changed Successfully'})
        else:
            messages.warning(request, get_errors_from_form(form))
        return redirect("accounts:new_password")
    

class ChangePassword(View):
    form = ChangePasswordForm()
    template_name = 'templates/accounts/change_password.html'

    
    def get(self, request):
        messages.info(request, "You must change your password")
        logging.debug("Change Password page requested" + request.get_full_path())
        return render(request, self.template_name, {'forms': self.form})

    def post(self, request):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password1 = form.cleaned_data.get('new_password1')
            new_password2 = form.cleaned_data.get('new_password2')
            if new_password1 == new_password2:
                user = request.user
                if user.check_password(old_password):
                    user.set_password(new_password1)
                    user.user_must_change_password = False
                    user.save()
                    update_session_auth_hash(request, user)
                    logging.debug(f"{request.user.username} User changed password successfully")
                    messages.success(request, "Password changed successfully")
                    logout(request)
                    return JsonResponse({'status': 'success', 'message': 'Password Changed Successfully'})
                else:
                    logging.debug(f"{request.user.username} User changed password failed. Password does not match")
                    messages.warning(request, "Old Password does not match")
            else:
                messages.warning(request, "New Password does not match")
        else:
            messages.warning(request, get_errors_from_form(form))
        return redirect("accounts:change_password")


