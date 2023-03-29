from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("attendance/", views.AttendanceRecord.as_view(), name="attendance"),
    path("attendance/<int:id>/", views.edit_attendance, name="edit_attendance"),
    path('chart/filter-options/', views.get_filter_options, name='chart-filter-options'),
    path('chart/data/leaders/<int:year>', views.get_leaders_chart, name='leaders_chart-data'),
    path('chart/data/first_timers/<int:year>', views.get_first_timers_chart, name='firsttimers_chart-data'),
    path('chart/data/members/<int:year>', views.get_members_chart, name='members_chart-data'),
    path('chart/data/consistency/<int:year>', views.get_consistency_chart, name='consistency_chart-data'),
    ]
