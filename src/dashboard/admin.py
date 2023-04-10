from django.contrib import admin
from dashboard.models import Attendance

# Register your models here.

from django.contrib.admin import SimpleListFilter
import datetime

class MonthFilter(SimpleListFilter):
    title = 'Month'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        return (
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        )

    def queryset(self, request, queryset):
        if self.value():
            month = int(self.value())
            return queryset.filter(date__month=month)
        return queryset

class AttendanceAdmin(admin.ModelAdmin):
    list_filter = (MonthFilter, 'branch')

admin.site.register(Attendance, AttendanceAdmin)
