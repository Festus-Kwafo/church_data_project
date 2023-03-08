from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.html import strip_tags
from django.views import View
from django.utils.decorators import method_decorator
from .forms import AtttendanceForms
from .models import Attendance
from accounts.models import User
from datetime import date
from django.db.models import Sum
# Create your views here.

class IndexView(View):
    template_name = 'templates/dashboard/index.html'
    today = date.today()

    @method_decorator(login_required(login_url="accounts:login"))
    def get(self, request):

        user = request.user
        branch_data = Attendance.objects.filter(branch_id = user.id)
        month_data = branch_data.filter(date__year=self.today.year, date__month=self.today.month).all().aggregate(Sum('total'))
        last_month_data = branch_data.filter(date__year=self.today.year, date__month=self.today.month - 1).all().aggregate(Sum('total'))
        latest_data = branch_data.order_by('date')[0]
        pre_sun_data = branch_data.order_by('date')[1]
        
        #Calulate Monthly percentage increase
        month_inc_percent =((month_data.get('total__sum')-last_month_data.get('total__sum'))/last_month_data.get('total__sum'))*100
        
        #Calculate previous sunday increase
        pre_sun_percent = ((int(latest_data.total)-int(pre_sun_data.total))/int(pre_sun_data.total))*100
        context = {"user": user, "latest_data": latest_data, 'month_data':month_data, "month_inc_percent": float(month_inc_percent), "pre_sun_percent": float(pre_sun_percent) }
        return render(request, self.template_name, context)

    def post(self, request):
        return redirect()

class AttendanceRecord(View):
    template_name = 'templates/dashboard/attendance_forms.html'
    form_class = AtttendanceForms
    @method_decorator(login_required(login_url="accounts:login"))
    def get(self, request):
        context = {"forms": self.form_class}
        return render(request, self.template_name, context)

    def post(self, request):
        forms = self.form_class(request.POST or None)
        user = request.user
        branch_data = Attendance.objects.filter(branch_id = user.id)
        latest_data = branch_data.order_by('date')[0]
        if request.POST.get("confirm")== "1" and forms.is_valid():
            data = forms.save(commit=False)
            data.branch = User(id=user.id)
            data.save()
            context = {"branch_data": branch_data, 'latest_data': latest_data}
            return redirect("dashboard:index")
        else:
            for field, error in forms.errors.items():
                message = f"{field.title()}: {strip_tags(error)}"
                break
            context = {k: v for k, v in request.POST.items()}
            messages.warning(request, message)
            print("Form is probably not valid")
        return render(request, self.template_name)