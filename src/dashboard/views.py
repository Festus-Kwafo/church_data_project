import json
import logging
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View
from django.db.models import FloatField
from django.db.models.functions import Cast
from django.contrib.auth.mixins import PermissionRequiredMixin

from accounts.models import User
from dashboard.chart import colorPrimary, get_year_dict, months
from dashboard.filter import data_filter, previous_sunday, two_previous_sunday

from .forms import AttendanceForms, SundayAttendanceForms, WednesdayAttendanceForms
from .models import Attendance, SundayAttendance,  WednesdayAttendance

logger = logging.getLogger("core")
import traceback

class IndexView(View):
    template_name = 'templates/dashboard/index.html'
    today = date.today()

    @method_decorator(login_required(login_url="accounts:login"))
    def get(self, request):
        user = request.user
        branch_data = SundayAttendance.objects.select_related('attendance').filter(attendance__branch_id=user.id)
        if not branch_data.filter(date=previous_sunday()).exists():
            logger.debug("No data for previous sunday", extra={'user': request.user.branch_name})
            messages.warning(request, 'Please update attendance for previous sunday')
            return redirect('dashboard:sunday_attendance')
        if not branch_data.filter(date=two_previous_sunday()).exists():
            logger.debug("No data for two previous sunday", extra={'user': request.user.branch_name})
            messages.warning(request, 'Please update attendance for two previous sunday')
            return redirect('dashboard:sunday_attendance')
        try:
            last_branch_data = SundayAttendance.objects.select_related('attendance').filter(attendance__branch_id=user.id).order_by('-date')[:5]
            # Attendance
            month_data = branch_data.filter(date__year=self.today.year, date__month=self.today.month).all().aggregate(
                Sum('attendance__total'))
            last_month_data = branch_data.filter(date__year=self.today.year,
                                                 date__month=self.today.month - 1).all().aggregate(Sum('attendance__total'))

            latest_data = SundayAttendance.objects.select_related('attendance').filter(attendance__branch_id=user.id, date=previous_sunday()).first()
            pre_sun_data = SundayAttendance.objects.select_related('attendance').filter(attendance__branch_id=user.id, date=two_previous_sunday()).first()

            # Calulate Monthly percentage increase
            month_inc_percent = ((month_data.get('attendance__total__sum') - last_month_data.get(
                'attendance__total__sum')) / last_month_data.get(
                'attendance__total__sum')) * 100

            # Calculate previous sunday increase
            pre_sun_percent = ((int(latest_data.attendance.total) - int(pre_sun_data.attendance.total)) / int(pre_sun_data.attendance.total)) * 100

            # First_timers
            first_timers_data = branch_data.filter(date__year=self.today.year,
                                                   date__month=self.today.month).all().aggregate(
                Sum('attendance__first_timers'))
            last_month_first_timers_data = branch_data.filter(date__year=self.today.year,
                                                              date__month=self.today.month - 1).all().aggregate(
                Sum('attendance__first_timers'))
            # Calulate Monthly percentage increase
            first_timers_month_inc_percent = ((first_timers_data.get(
                'attendance__first_timers__sum') - last_month_first_timers_data.get(
                'attendance__first_timers__sum')) / last_month_first_timers_data.get(
                'attendance__first_timers__sum')) * 100

            # Calculate previous sunday increase
            first_timers_pre_sun_percent = ((int(latest_data.attendance.first_timers) - int(pre_sun_data.attendance.first_timers)) / int(
                pre_sun_data.attendance.first_timers)) * 100

            # consistency
            consistency_data = branch_data.filter(date__year=self.today.year,
                                                  date__month=self.today.month).all().aggregate(
                Sum('consistency'))
            last_month_consistency_data = branch_data.filter(date__year=self.today.year,
                                                             date__month=self.today.month - 1).all().aggregate(
                Sum('consistency'))
            # Calulate Monthly percentage increase
            consistency_month_inc_percent = ((consistency_data.get(
                'consistency__sum') - last_month_consistency_data.get(
                'consistency__sum')) / last_month_consistency_data.get(
                'consistency__sum')) * 100

            # Calculate previous sunday increase
            consistency_pre_sun_percent = ((int(latest_data.consistency) - int(pre_sun_data.consistency)) / int(
                pre_sun_data.consistency)) * 100
        except Exception:
            print(traceback.format_exc())
            messages.warning(request, 'Error occurred while processing data')
            return redirect('dashboard:sunday_attendance')

        context = {"user": user, "latest_data": latest_data, 'last_branch_data': last_branch_data,
                   'month_data': month_data,
                   "month_inc_percent": round(month_inc_percent, 2), "pre_sun_percent": round(pre_sun_percent, 2),
                   'first_timers_data': first_timers_data,
                   'first_timers_month_inc_percent': round(first_timers_month_inc_percent, 2),
                   'first_timers_pre_sun_percent': round(first_timers_pre_sun_percent, 2),
                   'consistency_data': consistency_data,
                   'consistency_month_inc_percent': round(consistency_month_inc_percent, 2),
                   'consistency_pre_sun_percent': round(consistency_pre_sun_percent, 2)}
        return render(request, self.template_name, context)

    def post(self, request):
        try:
            if request.POST.get('filter_type') == 'attendance':
                return data_filter(request, 'total')
            elif request.POST.get('filter_type') == 'first_timers':
                return data_filter(request, 'first_timers')
            elif request.POST.get('filter_type') == 'consistency':
                return data_filter(request, 'consistency')
        except Exception as e:
            logger.debug(e)
            message = 'Error occurred while filtering data'
            messages.warning(request, message)
            return redirect("dashboard:attendance")


class SundayAttendanceRecord(View):
    template_name = 'templates/dashboard/forms/attendance_forms.html'
    form_class_1 = SundayAttendanceForms
    form_class_2= AttendanceForms

    @method_decorator(login_required(login_url="accounts:login"))
    def get(self, request):
        context = {"sunday_attendance_forms": self.form_class_1, "attendance_forms": self.form_class_2}
        return render(request, self.template_name, context)

    def post(self, request):
        sunday_attendance_forms = self.form_class_1(request.POST or None)
        attendance_forms = self.form_class_2(request.POST or None)
        user = request.user
        input_date = request.POST.get("date")
        female = request.POST.get("females")
        male = request.POST.get("males")
        adults = request.POST.get("adults")
        children = request.POST.get("children")
        context = {"sunday_attendance_forms": sunday_attendance_forms, "attendance_forms": attendance_forms}
        if sunday_attendance_forms.is_valid() and attendance_forms.is_valid():
            attendance_data = attendance_forms.save(commit=False)
            attendance_data.branch = user
            if SundayAttendance.objects.filter(date=input_date, attendance=attendance_data).exists():
                message = 'Data with this date already recorded. Check the dashboard to update it'
                messages.warning(request, message)
                return render(request, self.template_name, context)
            if int(female) + int(male) > int(adults) + int(children):
                message = 'Total number of people cannot be greater than the sum of adults and children'
                messages.warning(request, message)
                return render(request, self.template_name, context)
            if int(adults) + int(children) > int(female) + int(male):
                message = "Sum of adults and children cannot be greater than the total number of people"
                messages.warning(request, message)
                return render(request, self.template_name, context)
            sunday_attendance_data = sunday_attendance_forms.save(commit=False)
            sunday_attendance_data.attendance = attendance_data
            attendance_data.save()
            sunday_attendance_data.save()
            return redirect("dashboard:index")
        else:
            for field, error in sunday_attendance_forms.errors.items():
                logger.debug(error)
                message1 = f"{strip_tags(error)} {field}"
                messages.warning(request, message1)
                break
            for field, error in attendance_forms.errors.items():
                logger.debug(error)
                message2 = f"{strip_tags(error)} {field}"
                messages.warning(request, message2)
                break
        return render(request, self.template_name, context)



class WednesdayAttendanceRecord(PermissionRequiredMixin, View):
    template_name = 'templates/dashboard/forms/wednesday_attendance_forms.html'
    form_class_1 = WednesdayAttendanceForms
    form_class_2 = AttendanceForms
    permission_required = 'dashboard.add_midweek_record'
    login_url = 'accounts:login'

    def get(self, request):
        context = {"wednesday_attendance_forms": self.form_class_1, "attendance_forms": self.form_class_2}
        return render(request, self.template_name, context)

    def post(self, request):
        wednesday_attendance_forms = self.form_class_1(request.POST or None)
        attendance_forms = self.form_class_2(request.POST or None)
        user = request.user
        input_date = request.POST.get("date")
        female = request.POST.get("females")
        male = request.POST.get("males")
        adults = request.POST.get("adults")
        children = request.POST.get("children")
        if wednesday_attendance_forms.is_valid() and attendance_forms.is_valid():
            attendance_data = attendance_forms.save(commit=False)
            attendance_data.branch = user
            if WednesdayAttendance.objects.filter(date=input_date, attendance=attendance_data).exists():
                message = 'Data with this date already recorded. Check the dashboard to update it'
                messages.warning(request, message)
                return render(request, self.template_name)
            if int(female) + int(male) > int(adults) + int(children):
                message = 'Total number of people cannot be greater than the sum of adults and children'
                messages.warning(request, message)
                return render(request, self.template_name)
            if int(adults) + int(children) > int(female) + int(male):
                message = "Sum of adults and and children cannot be greater than the total number of people"
                messages.warning(request, message)
                return render(request, self.template_name)
            wednesday_attendance_data = wednesday_attendance_forms.save(commit=False)
            wednesday_attendance_data.attendance = attendance_data
            attendance_data.save()
            wednesday_attendance_data.save()
            return redirect("dashboard:index")
        else:
            for field, error in wednesday_attendance_forms.errors.items():
                message = f"{strip_tags(error)}"
                break
            for field, error in attendance_forms.errors.items():
                message = f"{strip_tags(error)}"
                break
            context = {k: v for k, v in request.POST.items()}
            messages.warning(request, message)
        return render(request, self.template_name, context)

def edit_attendance(request, id):
    sunday_attendance_instance = get_object_or_404(SundayAttendance, id=id)
    attendance_instance = get_object_or_404(Attendance, id=sunday_attendance_instance.attendance.id)
    female = request.POST.get("females")
    male = request.POST.get("males")
    adults = request.POST.get("adults")
    children = request.POST.get("children")
    if request.method == 'POST':
        sunday_attendance_forms = SundayAttendanceForms(request.POST, instance=sunday_attendance_instance)
        attendance_forms = AttendanceForms(request.POST, instance=attendance_instance)
        if sunday_attendance_forms.is_valid() and attendance_forms.is_valid():
            if int(female) + int(male) > int(adults) + int(children):
                message = 'Total number of people cannot be greater than the sum of adults and children'
                messages.warning(request, message)
                sunday_attendance_forms = SundayAttendanceForms( instance=sunday_attendance_instance)
                attendance_forms = AttendanceForms(instance=sunday_attendance_instance)
                return render(request, 'templates/dashboard/forms/attendance_forms_edit.html', {'sunday_attendance_forms': sunday_attendance_forms, 'attendance_forms': attendance_forms})
            if int(adults) + int(children) > int(female) + int(male):
                message = "Sum of adults and and children cannot be greater than the total number of people"
                messages.warning(request, message)
                sunday_attendance_forms = SundayAttendanceForms(instance=sunday_attendance_instance)
                attendance_forms = AttendanceForms(instance=sunday_attendance_instance)
                return render(request, 'templates/dashboard/forms/attendance_forms_edit.html',
                              {'sunday_attendance_forms': sunday_attendance_forms,
                               'attendance_forms': attendance_forms})
            sunday_attendance_data = sunday_attendance_forms.save(commit=False)
            sunday_attendance_data.save()
            return redirect('dashboard:index')
    else:
        sunday_attendance_forms = SundayAttendanceForms(instance=sunday_attendance_instance)
        attendance_forms = AttendanceForms(instance=attendance_instance)
    return render(request, 'templates/dashboard/forms/attendance_forms_edit.html',
                  {'sunday_attendance_forms': sunday_attendance_forms, 'attendance_forms': attendance_forms})



def edit_wednesday_attendance(request, id):
    wednesday_attendance_instance = get_object_or_404(SundayAttendance, id=id)
    attendance_instance = get_object_or_404(Attendance, id=wednesday_attendance_instance.attendance.id)
    female = request.POST.get("females")
    male = request.POST.get("males")
    adults = request.POST.get("adults")
    children = request.POST.get("children")
    if request.method == 'POST':
        wednesday_attendance_forms = SundayAttendanceForms(request.POST, instance=wednesday_attendance_instance)
        attendance_forms = AttendanceForms(request.POST, instance=attendance_instance)
        if wednesday_attendance_forms.is_valid() and attendance_forms.is_valid():
            if int(female) + int(male) > int(adults) + int(children):
                message = 'Total number of people cannot be greater than the sum of adults and children'
                messages.warning(request, message)
                wednesday_attendance_forms = SundayAttendanceForms( instance=wednesday_attendance_instance)
                attendance_forms = AttendanceForms(instance=wednesday_attendance_instance)
                return render(request, 'templates/dashboard/forms/attendance_forms_edit.html', {'sunday_attendance_forms': wednesday_attendance_forms, 'attendance_forms': attendance_forms})
            if int(adults) + int(children) > int(female) + int(male):
                message = "Sum of adults and and children cannot be greater than the total number of people"
                messages.warning(request, message)
                wednesday_attendance_forms = SundayAttendanceForms(instance=wednesday_attendance_instance)
                attendance_forms = AttendanceForms(instance=wednesday_attendance_instance)
                return render(request, 'templates/dashboard/forms/attendance_forms_edit.html',
                              {'sunday_attendance_forms': wednesday_attendance_forms,
                               'attendance_forms': attendance_forms})
            sunday_attendance_data = wednesday_attendance_forms.save(commit=False)
            sunday_attendance_data.save()
            return redirect('dashboard:index')
    else:
        wednesday_attendance_forms = SundayAttendanceForms(instance=wednesday_attendance_instance)
        attendance_forms = AttendanceForms(instance=attendance_instance)
    return render(request, 'templates/dashboard/forms/attendance_forms_edit.html',
                  {'sunday_attendance_forms': wednesday_attendance_forms, 'attendance_forms': attendance_forms})


def custom_page_not_found(request, exception):
    return render(request, 'templates/dashboard/pages-error-404.html', status=404)


def get_filter_options(request):
    try:
        grouped_purchases = SundayAttendance.objects.annotate(year=ExtractYear('date')).values('year').order_by(
            '-year').distinct()
        options = [purchase['year'] for purchase in grouped_purchases]

        return JsonResponse({
            'options': options,
        })
    except Exception as e:
        logger.info(e)


def get_leaders_chart(request, year):
    branch_id = request.user.id

    leaders = SundayAttendance.objects.select_related('attendance').filter(date__year=year).filter(attendance__branch_id=branch_id).annotate(
        month=ExtractMonth('date')).values('month').annotate(total_leaders=Sum('attendance__leaders')).values('month',
                                                                                                  'total_leaders').order_by(
        'month')
    sales_dict = get_year_dict()
    for group in leaders:
        sales_dict[months[group['month'] - 1]] = round(group['total_leaders'], 2)

    return JsonResponse({
        'title': f'Leaders Attendance in {year}',
        'data': {
            'labels': list(get_year_dict().keys()),
            'datasets': [{
                'label': 'Leaders Attendance',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(sales_dict.values()),
            }]
        },
    })


def get_first_timers_chart(request, year):
    branch_id = request.user.id
    first_timers = SundayAttendance.objects.select_related('attendance').filter(date__year=year).filter(attendance__branch_id=branch_id).annotate(
        month=ExtractMonth('date')).values('month').annotate(total_first_timers=Sum('attendance__first_timers')).values('month',
                                                                                                            'total_first_timers').order_by(
        'month')
    sales_dict = get_year_dict()
    for group in first_timers:
        sales_dict[months[group['month'] - 1]] = round(group['total_first_timers'], 2)

    return JsonResponse({
        'title': f'First Timers Attendance in {year}',
        'data': {
            'labels': list(sales_dict.keys()),
            'datasets': [{
                'label': 'First Timers Attendance',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(sales_dict.values()),
            }]
        },
    })


def get_consistency_chart(request, year):
    branch_id = request.user.id
    consistency = SundayAttendance.objects.select_related('attendance').filter(date__year=year).filter(attendance__branch_id=branch_id).annotate(
        month=ExtractMonth('date')).values('month').annotate(total_consistency=Sum('consistency')).values('month', 'total_consistency').order_by(
        'month')
    sales_dict = get_year_dict()
    for group in consistency:
        sales_dict[months[group['month'] - 1]] = round(group['total_consistency'], 2)

    return JsonResponse({
        'title': f'Consistency Attendance in {year}',
        'data': {
            'labels': list(sales_dict.keys()),
            'datasets': [{
                'label': 'Consistency Attendance',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(sales_dict.values()),
            }]
        },
    })


def get_members_chart(request, year):
    branch_id = request.user.id
    members = SundayAttendance.objects.select_related('attendance').filter(date__year=year).filter(attendance__branch_id=branch_id).annotate(
        month=ExtractMonth('date')).values('month').annotate(total_members=Cast(Sum('attendance__total')- Sum('attendance__leaders'), output_field=FloatField())).values(
        'month', 'total_members').order_by('month')
    sales_dict = get_year_dict()
    for group in members:
        sales_dict[months[group['month'] - 1]] = round(group['total_members'], 2)

    return JsonResponse({
        'title': f'Members Attendance in {year}',
        'data': {
            'labels': list(sales_dict.keys()),
            'datasets': [{
                'label': 'Members Attendance',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(sales_dict.values()),
            }]
        },
    })


# Random Colors Generator


