# Generated by Django 4.2.1 on 2023-11-25 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_rename_birth_date_user_planted_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_must_change_password',
            field=models.BooleanField(default=True),
        ),
    ]
