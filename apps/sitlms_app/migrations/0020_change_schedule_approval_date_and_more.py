# Generated by Django 4.2 on 2023-05-16 03:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0019_rename_frequency_change_schedule_new_frequency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='change_schedule',
            name='approval_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='change_schedule',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 16, 11, 7, 35, 44030)),
        ),
    ]