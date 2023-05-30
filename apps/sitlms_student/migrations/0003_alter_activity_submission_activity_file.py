# Generated by Django 4.2 on 2023-05-29 10:48

import apps.sitlms_student.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_student', '0002_alter_activity_submission_grade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity_submission',
            name='activity_file',
            field=models.FileField(blank=True, upload_to=apps.sitlms_student.models.activity_attachment_path, validators=[apps.sitlms_student.models.validate_file_size]),
        ),
    ]
