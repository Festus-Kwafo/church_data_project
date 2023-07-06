from django.db import models

from accounts.models import User

# Create your models here.
class Attendance(models.Model):
    branch = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    adults = models.IntegerField()
    females = models.IntegerField()
    males = models.IntegerField()
    leaders = models.IntegerField()
    children = models.IntegerField()
    first_timers = models.IntegerField()
    total = models.IntegerField()
    @property
    def cal_total(self):
        return int(self.adults) + int(self.children)

    def save(self, *args, **kwarg):
        self.total = self.cal_total
        super().save(*args, **kwarg)
    def __str__(self):
        return self.branch.branch

    class Meta:
        db_table = "attendance"

class SundayAttendance(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='sunday_attendance')
    consistency = models.IntegerField()
    offering = models.DecimalField(decimal_places=2, max_digits=10)
    tithe = models.DecimalField(decimal_places=2, max_digits=10)
    approved = models.BooleanField(default=False)
    # Ratio
    leaders_to_members = models.CharField(max_length=6, default="0:0")
    leaders_to_offering = models.CharField(max_length=6, default="0:0")
    members_to_offering = models.CharField(max_length=6, default="0:0")

    date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    @property
    def leaders_to_members_ratio(self):
        def find_gcd(numerator, denominator):
            if numerator == 0:
                return denominator
            return find_gcd(denominator % numerator, numerator)

        numerator = int(self.attendance.leaders)
        denominator = int(self.attendance.total) - int(self.attendance.leaders)

        gcd = find_gcd(numerator, denominator)

        a = numerator // gcd
        b = denominator // gcd

        return f"{a}:{b}"

    @property
    def leaders_to_offering_ratio(self):
        def find_gcd(numerator, denominator):
            if numerator == 0:
                return denominator
            return find_gcd(denominator % numerator, numerator)

        numerator = int(self.attendance.leaders)
        denominator = round(self.offering)

        gcd = find_gcd(numerator, denominator)

        a = numerator // gcd
        b = denominator // gcd

        return f"{a}:{b}"

    @property
    def members_to_offering_ratio(self):
        def find_gcd(numerator, denominator):
            if numerator == 0:
                return denominator
            return find_gcd(denominator % numerator, numerator)

        numerator = int(self.attendance.total) - int(self.attendance.leaders)
        denominator = round(self.offering)

        gcd = find_gcd(numerator, denominator)

        a = numerator // gcd
        b = denominator // gcd

        return f"{a}:{b}"

    def save(self, *args, **kwarg):
        self.leaders_to_members = self.leaders_to_members_ratio
        self.leaders_to_offering = self.leaders_to_offering_ratio
        self.members_to_offering = self.members_to_offering_ratio
        super(SundayAttendance, self).save(*args, **kwarg)

    class Meta:
        db_table = "sunday_attendance"


class WednesdayAttendance(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='wednesday_attendance')
    offering = models.DecimalField(decimal_places=2, max_digits=10)
    approved = models.BooleanField(default=False)

    date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    def __str__(self):
        return self.attendance.branch.branch + " " + str(self.date)

    class Meta:
        db_table = "wednesday_attendance"


class SpecialEventAttendance(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='special_event_attendance')
    service_name = models.CharField(max_length=100)
    offering = models.DecimalField(decimal_places=2, max_digits=10)
    approved = models.BooleanField(default=False)

    date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.service_name + " " + str(self.date)

    class Meta:
        db_table = "special_event_attendance"

class DashboardPermission(models.Model):
    class Meta:
        permissions = [
            ("add_midweek_record", "Can add midweek record"),
        ]

