# Generated by Django 4.2 on 2023-05-30 03:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sitlms_instructor', '0005_alter_activity_comments_timestamp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityprivatecomments',
            name='uid',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]