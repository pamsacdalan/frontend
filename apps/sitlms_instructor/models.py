from django.db import models
from apps.sitlms_app.models import Course_Enrollment, Instructor_Auth, Students_Auth
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

def activity_attachment_path(instance, filename):
    return 'activity_attachment/{}_{}/{}'.format(instance.course_batch, instance.activity_title, filename)

def validate_file_size(value):
    # Specify the maximum file size in bytes
    # Push 20230529: This is not used. Checking is in views.py
    max_size = 25 * 1024 * 1024  # 10MB

    if value.size > max_size:
        raise ValidationError("File size exceeds the maximum allowed size of 25MB.")

# Create your models here.
class Course_Announcement(models.Model):
    course_batch = models.ForeignKey(Course_Enrollment, on_delete=models.CASCADE)
    announcement_text = models.CharField(max_length=1000)
    date_posted = models.DateTimeField(default=datetime.now, blank=True)
    author = models.ForeignKey(Instructor_Auth, on_delete=models.CASCADE)

class Course_Activity(models.Model):
    course_batch = models.ForeignKey(Course_Enrollment, on_delete=models.CASCADE)
    activity_title = models.CharField(max_length=255)
    activity_desc = models.CharField(max_length=1000)
    activity_attachment = models.FileField(upload_to=activity_attachment_path, blank=True, validators=[validate_file_size])
    start_date = models.DateTimeField(default=timezone.now, blank=True)
    deadline = models.DateTimeField()
    max_score = models.IntegerField()
    grading_percentage = models.DecimalField(decimal_places=2,max_digits=5)

class Activity_Comments(models.Model):
    course_activity = models.ForeignKey(Course_Activity, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField()
    timestamp = models.DateTimeField(default=timezone.now)

class ActivityPrivateComments(models.Model):
    course_activity = models.ForeignKey(Course_Activity, on_delete=models.CASCADE)
    student = models.ForeignKey(Students_Auth, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
