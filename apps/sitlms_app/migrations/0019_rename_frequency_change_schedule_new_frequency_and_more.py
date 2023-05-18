# Generated by Django 4.2 on 2023-05-16 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0018_change_schedule_frequency'),
    ]

    operations = [
        migrations.RenameField(
            model_name='change_schedule',
            old_name='frequency',
            new_name='new_frequency',
        ),
        migrations.AddField(
            model_name='change_schedule',
            name='old_frequency',
            field=models.IntegerField(null=True),
        ),
    ]
