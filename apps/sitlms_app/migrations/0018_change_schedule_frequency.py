# Generated by Django 4.2 on 2023-05-15 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0017_alter_change_schedule_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='change_schedule',
            name='frequency',
            field=models.IntegerField(null=True),
        ),
    ]
