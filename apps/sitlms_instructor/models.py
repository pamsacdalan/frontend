from django.db import models
from apps.sitlms_app.models import Course_Enrollment, Instructor_Auth
from datetime import datetime
from django.contrib.auth.models import User

def activity_attachment_path(instance, filename):
    return 'activity_attachment/{}_{}/{}'.format(instance.course_batch, instance.activity_title, filename)

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
    activity_attachment = models.FileField(upload_to=activity_attachment_path, blank=True)
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    deadline = models.DateTimeField()
    max_score = models.IntegerField()
    grading_percentage = models.DecimalField(decimal_places=2,max_digits=5)

class Activity_Comments(models.Model):
    course_activity = models.ForeignKey(Course_Activity, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField()
    timestamp = models.DateTimeField(default=datetime.now)