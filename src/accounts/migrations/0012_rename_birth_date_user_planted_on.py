# Generated by Django 4.2.1 on 2023-11-23 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_user_country'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='birth_date',
            new_name='planted_on',
        ),
    ]
