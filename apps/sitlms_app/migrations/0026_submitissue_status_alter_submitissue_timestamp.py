# Generated by Django 4.2 on 2023-05-30 05:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0025_submitissue'),
    ]

    operations = [
        migrations.AddField(
            model_name='submitissue',
            name='status',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='submitissue',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 30, 13, 33, 20, 184712)),
        ),
    ]
