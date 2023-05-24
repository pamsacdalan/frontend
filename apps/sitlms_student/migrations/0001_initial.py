# Generated by Django 4.2 on 2023-05-23 05:35

import apps.sitlms_student.models
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sitlms_app', '0022_merge_20230517_1725'),
        ('sitlms_instructor', '0003_course_activity_max_score_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity_Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_submitted', models.DateTimeField(default=datetime.datetime.now)),
                ('grade', models.IntegerField(blank=True)),
                ('activity_file', models.FileField(blank=True, upload_to=apps.sitlms_student.models.activity_attachment_path)),
                ('course_activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sitlms_instructor.course_activity')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sitlms_app.students_auth')),
            ],
        ),
    ]
