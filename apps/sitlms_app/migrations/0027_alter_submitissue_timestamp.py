# Generated by Django 4.2 on 2023-05-30 07:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0026_submitissue_status_alter_submitissue_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submitissue',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 30, 15, 10, 50, 252412)),
        ),
    ]