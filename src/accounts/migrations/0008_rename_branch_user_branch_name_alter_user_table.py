# Generated by Django 4.2.1 on 2023-07-06 00:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_user_otp_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='branch',
            new_name='branch_name',
        ),
        migrations.AlterModelTable(
            name='user',
            table='branches',
        ),
    ]
