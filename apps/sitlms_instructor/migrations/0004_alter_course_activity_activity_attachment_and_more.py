# Generated by Django 4.2 on 2023-05-29 10:48

import apps.sitlms_instructor.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_instructor', '0003_course_activity_max_score_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course_activity',
            name='activity_attachment',
            field=models.FileField(blank=True, upload_to=apps.sitlms_instructor.models.activity_attachment_path, validators=[apps.sitlms_instructor.models.validate_file_size]),
        ),
        migrations.AlterField(
            model_name='course_activity',
            name='start_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
