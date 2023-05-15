from django.db import models
from apps.sitlms_app.models import Course_Enrollment, Instructor_Auth
from datetime import datetime

'''
def activity_attachment_path(instance, filename):
    return 'activity_attachment/{}_{}_{}/{}'.format(instance.id, instance.course_batch, instance.activity_title, filename)
'''

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
    activity_attachment = models.URLField(max_length=200)
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    deadline = models.DateTimeField()
    grading_percentage = models.IntegerField()

