
from django.http import JsonResponse
from .models import Attendance
from datetime import date
from django.db.models import Sum

def data_filter(request, type):
    today = date.today()
    user = request.user
    branch_data = Attendance.objects.filter(branch_id=user.id)
    if request.POST.get('filter_input') == 'today':
        if type == 'total':
            latest_data = branch_data.order_by('date')[0].total
            pre_sun_data = branch_data.order_by('date')[1].total
        elif type == 'first_timers':
            latest_data = branch_data.order_by('date')[0].first_timers
            pre_sun_data = branch_data.order_by('date')[1].first_timers
        elif type == 'consistency':
            latest_data = branch_data.order_by('date')[0].consistency
            pre_sun_data = branch_data.order_by('date')[1].consistency
        # Calculate previous sunday increase
        pre_sun_percent = ((int(latest_data) - int(pre_sun_data)) / int(pre_sun_data)) * 100
        response = JsonResponse({"total": latest_data, "percentage": pre_sun_percent})
        return response
    elif request.POST.get('filter_input') == 'this_month':
        month_data = branch_data.filter(date__year=today.year, date__month=today.month).all().aggregate(
            Sum(type))
        last_month_data = branch_data.filter(date__year=today.year,
                                             date__month=today.month - 1).all().aggregate(Sum(type))

        # Calulate Monthly percentage increase
        month_inc_percent = ((month_data.get(type+'__sum') - last_month_data.get(
            type+'__sum')) / last_month_data.get(
            type+'__sum')) * 100
        response = JsonResponse({'total': month_data.get(type+'__sum'), "percentage": round(month_inc_percent, 2)})
        return response
    elif request.POST.get('filter_input') == 'this_year':
        year_data = branch_data.filter(date__year=today.year).all().aggregate(
            Sum(type))
        last_year_data = branch_data.filter(date__year=today.year - 1).all().aggregate(Sum(type))

        # Calulate Monthly percentage increase
        year_inc_percent = ((year_data.get(type+'__sum') - last_year_data.get(type+'__sum')) / last_year_data.get(
            type+'__sum')) * 100
        response = JsonResponse({'total': year_data.get(type+'__sum'), "percentage": round(float(year_inc_percent), 2)})
        return response
