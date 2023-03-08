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
    total = models.CharField(max_length=6)
    date = models.DateField()
    

    @property
    def cal_total(self):
        return int(self.adults) + int(self.children)
    
    def save(self, *args, **kwarg):
        self.total = self.cal_total
        super(Attendance, self).save(*args, **kwarg)

    def __str__(self):
        return self.branch