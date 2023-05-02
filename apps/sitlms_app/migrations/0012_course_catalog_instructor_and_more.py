# Generated by Django 4.2 on 2023-05-01 15:16

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sitlms_app', '0011_course_catalog_instructor_alter_students_access_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course_Catalog',
            fields=[
                ('course_id', models.AutoField(primary_key=True, serialize=False)),
                ('course_desc', models.CharField(max_length=100)),
                ('course_title', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('instructor_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('firstname', models.CharField(max_length=255)),
                ('middlename', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('birthdate', models.DateField()),
                ('active_deactive', models.BooleanField(default=True)),
                ('access_type', models.IntegerField(default=2)),
            ],
            options={
                'db_table': 'instructor',
            },
        ),
        migrations.AlterField(
            model_name='instructor_auth',
            name='access_type',
            field=models.IntegerField(default=3, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='students',
            name='access_type',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2)], default=0, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='students',
            name='active_deactive',
            field=models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=50),
        ),
        migrations.AlterField(
            model_name='students',
            name='birthdate',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='students',
            name='employment_status',
            field=models.CharField(choices=[('Deployed', 'Deployed'), ('Training', 'Training')], default='Deployed', max_length=50),
        ),
        migrations.CreateModel(
            name='Students_Auth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program_id', models.IntegerField()),
                ('student_no', models.CharField(max_length=7)),
                ('middlename', models.CharField(max_length=50)),
                ('birthdate', models.DateField()),
                ('employment_status', models.CharField(choices=[('Deployed', 'Deployed'), ('Training', 'Training')], default='Deployed', max_length=50)),
                ('active_deactive', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=50)),
                ('access_type', models.IntegerField(default=2, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Course_Enrollment',
            fields=[
                ('course_batch', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('instructor_id', models.IntegerField()),
                ('session_details', models.URLField(max_length=100)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('course_mode', models.IntegerField()),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sitlms_app.course_catalog')),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('middle_name', models.CharField(blank=True, max_length=255)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('access_type', models.IntegerField(default=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]