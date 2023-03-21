from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.html import strip_tags
from django.views import View
from django.utils.decorators import method_decorator
from .forms import AtttendanceForms
from .models import Attendance
from accounts.models import User
from datetime import date
from django.db.models import Sum
from dashboard.filter import data_filter, two_previous_sunday, previous_sunday
from django.core.exceptions import ValidationError
# Create your views here.

class IndexView(View):
    template_name = 'templates/dashboard/index.html'
    today = date.today()

    @method_decorator(login_required(login_url="accounts:login"))
    def get(self, request):
        user = request.user
        branch_data = Attendance.objects.filter(branch_id=user.id)
        try:
            #Attendance
            month_data = branch_data.filter(date__year=self.today.year, date__month=self.today.month).all().aggregate(
                Sum('total'))
            last_month_data = branch_data.filter(date__year=self.today.year,
                                                 date__month=self.today.month - 1).all().aggregate(Sum('total'))
            latest_data = Attendance.objects.filter(branch_id=user.id, date=previous_sunday()).first()
            pre_sun_data = Attendance.objects.filter(branch_id=user.id, date=two_previous_sunday()).first()

            # Calulate Monthly percentage increase
            month_inc_percent = ((month_data.get('total__sum') - last_month_data.get('total__sum')) / last_month_data.get(
                'total__sum')) * 100

            # Calculate previous sunday increase
            pre_sun_percent = ((int(latest_data.total) - int(pre_sun_data.total)) / int(pre_sun_data.total)) * 100

            #First_timers
            first_timers_data = branch_data.filter(date__year=self.today.year, date__month=self.today.month).all().aggregate(
                Sum('first_timers'))
            last_month_first_timers_data = branch_data.filter(date__year=self.today.year,
                                                 date__month=self.today.month - 1).all().aggregate(Sum('first_timers'))
            # Calulate Monthly percentage increase
            first_timers_month_inc_percent = ((first_timers_data.get('first_timers__sum') - last_month_first_timers_data.get('first_timers__sum')) / last_month_first_timers_data.get(
                'first_timers__sum')) * 100

            # Calculate previous sunday increase
            first_timers_pre_sun_percent = ((int(latest_data.first_timers) - int(pre_sun_data.first_timers)) / int(pre_sun_data.first_timers)) * 100

            # consistency
            consistency_data = branch_data.filter(date__year=self.today.year, date__month=self.today.month).all().aggregate(
                Sum('consistency'))
            last_month_consistency_data = branch_data.filter(date__year=self.today.year,
                                                             date__month=self.today.month - 1).all().aggregate(
                Sum('consistency'))
            # Calulate Monthly percentage increase
            consistency_month_inc_percent = ((consistency_data.get('consistency__sum') - last_month_consistency_data.get(
                'consistency__sum')) / last_month_consistency_data.get(
                'consistency__sum')) * 100

            # Calculate previous sunday increase
            consistency_pre_sun_percent = ((int(latest_data.consistency) - int(pre_sun_data.consistency)) / int(
                pre_sun_data.consistency)) * 100
        except:
            last_month_consistency_data = 0
            latest_data = 0
            month_data = 0
            month_inc_percent = 0
            pre_sun_percent = 0
            first_timers_pre_sun_percent = 0
            first_timers_data  = 0
            first_timers_month_inc_percent = 0
            consistency_data = 0
            consistency_month_inc_percent = 0
            consistency_pre_sun_percent = 0

        context = {"user": user, "latest_data": latest_data, 'month_data': month_data,
                   "month_inc_percent": round(month_inc_percent, 2), "pre_sun_percent": round(pre_sun_percent, 2), 'first_timers_data':first_timers_data, 'first_timers_month_inc_percent': round(first_timers_month_inc_percent, 2) , 'first_timers_pre_sun_percent':round(first_timers_pre_sun_percent, 2), 'consistency_data':consistency_data , 'consistency_month_inc_percent': round(consistency_month_inc_percent, 2), 'consistency_pre_sun_percent': round(consistency_pre_sun_percent, 2) }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        branch_data = Attendance.objects.filter(branch_id=user.id)
        if request.POST.get('filter_type') == 'attendance':
            return data_filter(request, 'total')
        elif request.POST.get('filter_type')== 'first_timers':
            return data_filter(request, 'first_timers')
        elif request.POST.get('filter_type') == 'consistency':
            return data_filter(request, 'consistency')
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
        input_date = request.POST.get("date")
        if request.POST.get("confirm") == "1" and forms.is_valid():
            if Attendance.objects.filter(date=input_date, branch_id=request.user.id).exists():
                message = 'Data with this date already recorded. Check the dashboard to update it'
                messages.warning(request, message)
                return render(request, self.template_name)
            data = forms.save(commit=False)
            data.branch = User(id=user.id)
            data.save()
            return redirect("dashboard:index")
        else:
            for field, error in forms.errors.items():
                message = f"{strip_tags(error)}"
                break
            context = {k: v for k, v in request.POST.items()}
            messages.warning(request, message)
        return render(request, self.template_name, context)


def custom_page_not_found(request, exception):
    return render(request, 'templates/dashboard/pages-error-404.html', status=404)
