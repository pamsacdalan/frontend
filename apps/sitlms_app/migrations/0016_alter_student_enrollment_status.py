# Generated by Django 4.2 on 2023-05-16 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0015_csv_program_course_enrollment_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student_enrollment',
            name='status',
            field=models.CharField(default='Ongoing', max_length=10),
        ),
    ]
