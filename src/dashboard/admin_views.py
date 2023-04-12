import calendar
import datetime
import random

from dateutil.relativedelta import relativedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render

from accounts.models import User

from .models import Attendance


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgba({r}, {g}, {b}, 0.2)', f'rgb({r}, {g}, {b})'


def months_dis(year):
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    months = []
    if year < current_year:
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
        return months
    elif year == current_year:
        for month in range(1, current_month + 1):
            month_name = datetime.date(year, month, 1).strftime('%B')
            months.append(month_name)
    else:
        months = []
    return months


def get_yearly_attendance(request, year):
    # Get all unique branches
    branches = Attendance.objects.values_list('branch__branch', flat=True).distinct()

    # Initialize the dataset
    datasets = []

    # Loop through the branches and get the total attendance for each branch
    for branch in branches:
        data = []
        for month in range(1, len(months_dis(year)) + 1):
            attendance_count = \
                Attendance.objects.filter(branch__branch=branch, date__year=year, date__month=month).aggregate(
                    Sum('total'))['total__sum'] or 0
            data.append(attendance_count)

        # You can set custom colors for each branch or use a color generator
        backgroundColor, borderColor = random_color()

        # Create the dataset for the current branch
        dataset = {
            'label': branch,
            'data': data,
            'borderColor': borderColor,
            'backgroundColor': backgroundColor,
        }

        # Append the dataset to the datasets list
        datasets.append(dataset)

    # Return the labels and datasets as a JSON response
    return JsonResponse({'title': f'Total Attendance in {year}', 'labels': months_dis(year), 'datasets': datasets})


def get_yearly_leaders(request, year):
    # Get all unique branches
    branches = Attendance.objects.values_list('branch__branch', flat=True).distinct()

    # Initialize the dataset
    datasets = []

    # Loop through the branches and get the total attendance for each branch
    for branch in branches:
        data = []
        for month in range(1, len(months_dis(year)) + 1):
            attendance_count = \
                Attendance.objects.filter(branch__branch=branch, date__year=year, date__month=month).aggregate(
                    Sum('leaders'))['leaders__sum'] or 0
            data.append(attendance_count)

        # You can set custom colors for each branch or use a color generator
        backgroundColor, borderColor = random_color()

        # Create the dataset for the current branch
        dataset = {
            'label': branch,
            'data': data,
            'borderColor': borderColor,
            'backgroundColor': backgroundColor,
        }

        # Append the dataset to the datasets list
        datasets.append(dataset)

    # Return the labels and datasets as a JSON response
    return JsonResponse({'title': f'Leaders Attendance in {year}', 'labels': months_dis(year), 'datasets': datasets})


def get_yearly_members(request, year):
    # Get all unique branches
    branches = Attendance.objects.values_list('branch__branch', flat=True).distinct()

    # Initialize the dataset
    datasets = []

    # Loop through the branches and get the total attendance for each branch
    for branch in branches:
        data = []
        for month in range(1, len(months_dis(year)) + 1):
            total_attendance_count = \
                Attendance.objects.filter(branch__branch=branch, date__year=year, date__month=month).aggregate(
                    Sum('total'))['total__sum'] or 0
            leaders_attendance_count = \
                Attendance.objects.filter(branch__branch=branch, date__year=year, date__month=month).aggregate(
                    Sum('leaders'))['leaders__sum'] or 0
            memeber_count = total_attendance_count - leaders_attendance_count
            data.append(memeber_count)

        # You can set custom colors for each branch or use a color generator
        backgroundColor, borderColor = random_color()

        # Create the dataset for the current branch
        dataset = {
            'label': branch,
            'data': data,
            'borderColor': borderColor,
            'backgroundColor': backgroundColor,
        }

        # Append the dataset to the datasets list
        datasets.append(dataset)

    # Return the labels and datasets as a JSON response
    return JsonResponse({'title': f'Members Attendance in {year}', 'labels': months_dis(year), 'datasets': datasets})


def get_yearly_firsttimers(request, year):
    # Get all unique branches
    branches = Attendance.objects.values_list('branch__branch', flat=True).distinct()

    # Initialize the dataset
    datasets = []

    # Loop through the branches and get the total attendance for each branch
    for branch in branches:
        data = []
        for month in range(1, len(months_dis(year)) + 1):
            attendance_count = \
                Attendance.objects.filter(branch__branch=branch, date__year=year, date__month=month).aggregate(
                    Sum('first_timers'))['first_timers__sum'] or 0
            data.append(attendance_count)

        # You can set custom colors for each branch or use a color generator
        backgroundColor, borderColor = random_color()

        # Create the dataset for the current branch
        dataset = {
            'label': branch,
            'data': data,
            'borderColor': borderColor,
            'backgroundColor': backgroundColor,
        }

        # Append the dataset to the datasets list
        datasets.append(dataset)

    # Return the labels and datasets as a JSON response
    return JsonResponse(
        {'title': f'First Timers Attendance in {year}', 'labels': months_dis(year), 'datasets': datasets})


@staff_member_required
def statistics_view(request):
    def count_sundays(year, month):
        # Create a calendar object for the specified month and year
        month_calendar = calendar.monthcalendar(year, month)
        # Count the number of Sundays in the calendar
        sundays_count = sum(1 for week in month_calendar if week[calendar.SUNDAY] != 0)
        return sundays_count

    current_date = datetime.datetime.now()
    previous_month_date = current_date - relativedelta(months=1)
    previous_month = previous_month_date.month
    total_attendance = Attendance.objects.filter(date__month=previous_month).aggregate(Sum('total'))['total__sum']
    total_firsttimers = Attendance.objects.filter(date__month=previous_month).aggregate(Sum('first_timers'))[
        'first_timers__sum']
    total_leaders = Attendance.objects.filter(date__month=previous_month).aggregate(Sum('leaders'))['leaders__sum']
    total_sundays = count_sundays(previous_month_date.year, previous_month)
    avg_attendance = total_attendance / total_sundays
    avg_firsttimers = total_firsttimers / total_sundays
    avg_leaders = total_leaders / total_sundays
    total_branches = User.objects.filter(is_staff=False).count()

    context = {
        'avg_attendance': round(avg_attendance),
        'total_branches': total_branches,
        'avg_firsttimers': round(avg_firsttimers),
        'avg_leaders': round(avg_leaders),
        'previous_month': previous_month_date.strftime("%B"),
    }
    return render(request, 'templates/dashboard/statistics.html', context)
