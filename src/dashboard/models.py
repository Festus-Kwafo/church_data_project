from django.db import models

from accounts.models import User


# Create your models here.
class Attendance(models.Model):
    branch = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    adults = models.CharField(max_length=6)
    females = models.CharField(max_length=6)
    males = models.CharField(max_length=6)
    leaders = models.CharField(max_length=6)
    children = models.CharField(max_length=6)
    approved = models.BooleanField(default=False)
    first_timers = models.CharField(max_length=6)
    consistency = models.CharField(max_length=6)
    offering = models.CharField(max_length=11)
    tithe = models.CharField(max_length=11)
    total = models.CharField(max_length=6)
    #Ratio
    leaders_to_members = models.CharField(max_length=6, default="0:0")
    leaders_to_offering = models.CharField(max_length=6, default="0:0")
    members_to_offering = models.CharField(max_length=6, default="0:0")

    date = models.DateField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    @property
    def cal_total(self):
        return int(self.adults) + int(self.children)

    @property
    def leaders_to_members_ratio(self):
        def find_gcd(numerator, denominator):
            if numerator == 0:
                return denominator
            return find_gcd(denominator % numerator, numerator)

        numerator = int(self.leaders)
        denominator = int(self.total) - int(self.leaders)

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

        numerator = int(self.leaders)
        denominator = round(float(self.offering))

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

        numerator = int(self.total) - int(self.leaders)
        denominator = round(float(self.offering))

        gcd = find_gcd(numerator, denominator)

        a = numerator // gcd
        b = denominator // gcd

        return f"{a}:{b}"

    def save(self, *args, **kwarg):
        self.total = self.cal_total
        self.leaders_to_members = self.leaders_to_members_ratio
        self.leaders_to_offering = self.leaders_to_offering_ratio
        self.members_to_offering = self.members_to_offering_ratio
        super(Attendance, self).save(*args, **kwarg)

    def __str__(self):
        return self.branch.branch
