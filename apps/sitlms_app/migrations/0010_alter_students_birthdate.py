# Generated by Django 4.2 on 2023-04-25 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0009_alter_students_student_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students',
            name='birthdate',
            field=models.DateField(verbose_name='Birthday'),
        ),
    ]