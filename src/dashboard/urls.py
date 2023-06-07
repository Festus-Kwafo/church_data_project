from django.urls import path

from . import admin_views, views

app_name = "dashboard"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("sunday/attendance/", views.SundayAttendanceRecord.as_view(), name="sunday_attendance"),
    path("sunday/attendance/<int:id>/", views.edit_attendance, name="edit_sunday_attendance"),
    path("wednesday/attendance/", views.WednesdayAttendanceRecord.as_view(), name="wednesday_attendance"),
    path("wednesday/attendance/<int:id>/", views.edit_wednesday_attendance, name="edit_wednesday_attendance"),
    path('chart/filter-options/', views.get_filter_options, name='chart-filter-options'),
    path('chart/data/leaders/<int:year>', views.get_leaders_chart, name='leaders_chart-data'),
    path('chart/data/first_timers/<int:year>', views.get_first_timers_chart, name='firsttimers_chart-data'),
    path('chart/data/members/<int:year>', views.get_members_chart, name='members_chart-data'),
    path('chart/data/consistency/<int:year>', views.get_consistency_chart, name='consistency_chart-data'),

    # Statistics views
    path('statistics/yearly-attendance/<int:year>', admin_views.get_yearly_attendance, name='yearly_attendance'),
    path('statistics/yearly-leaders/<int:year>', admin_views.get_yearly_leaders, name='yearly_leaders'),
    path('statistics/yearly-members/<int:year>', admin_views.get_yearly_members, name='yearly_members'),
    path('statistics/yearly-firsttimers/<int:year>', admin_views.get_yearly_firsttimers, name='yearly_firsttimers'),
    path('statistics/', admin_views.statistics_view, name='statistics'),
    ]
