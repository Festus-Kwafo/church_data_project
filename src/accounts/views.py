from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from .forms import RegistrationForm
from accounts.utils.functions import get_errors_from_form
from django.contrib.admin.views.decorators import staff_member_required

class LoginView(View):
    template_name = 'templates/accounts/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = "on" in request.POST.get("remember_me", "")
        user = authenticate(username=username, password=password)
        print(user)
        print(username +" "+ password)
        if user:
            login(request, user)
            if remember_me:
                request.session.set_expiry(86400 * 30)
            user.last_login = timezone.now()
            user.save()
            redirect_url = request.GET.get("next") or "dashboard:index"
            return redirect(redirect_url)
        else:
            context = {k: v for k, v in request.POST.items()}
            messages.warning(request, "Invalid credentials")
            return render(request, self.template_name, context)


@staff_member_required
class RegisterBranch(View):
    template_name = 'templates/accounts/register.html'

    def get(self, request):
        registerForm = RegistrationForm(request.POST)
        context = {'forms': registerForm}
        return render(self.request, self.template_name, context)
    
    def post(self, request):
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.created_at = timezone.now()
            user.save()
        else:
            error_message = get_errors_from_form(registerForm)
            messages.warning(request, error_message)
            return redirect('accounts:register')
        return redirect('accounts:login')
        
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')
