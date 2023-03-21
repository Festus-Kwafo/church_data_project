# Generated by Django 4.1.7 on 2023-03-16 10:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_alter_attendance_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='date_created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='date_updated',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='offering',
            field=models.CharField(default=1, max_length=11),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='tithe',
            field=models.CharField(default=1, max_length=11),
            preserve_default=False,
        ),
    ]
