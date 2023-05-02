# Generated by Django 4.2 on 2023-05-01 15:22

from django.db import migrations
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sitlms_app', '0012_course_catalog_instructor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students_auth',
            name='access_type',
            field=models.IntegerField(default=2, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='admin',
            name='access_type',
            field=models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)]),
        ),
    ]