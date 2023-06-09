from django.db import models
from apps.sitlms_app.models import Students_Auth
from apps.sitlms_instructor.models import Course_Activity
from datetime import datetime
from django.core.exceptions import ValidationError

def activity_attachment_path(instance, filename):
    return 'activity_submission/{}/{}/{}/{}'.format(instance.course_activity.course_batch, instance.course_activity, instance.student_id, filename)

def validate_file_size(value):
    # Specify the maximum file size in bytes
    max_size = 25 * 1024 * 1024  # 10MB

    if value.size > max_size:
        raise ValidationError("File size exceeds the maximum allowed size of 25MB.")


# Create your models here.
class Activity_Submission(models.Model):
    course_activity = models.ForeignKey(Course_Activity, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(default=datetime.now)
    grade = models.IntegerField(blank=True, null=True)
    student_id = models.ForeignKey(Students_Auth, on_delete=models.CASCADE)
    activity_file = models.FileField(upload_to=activity_attachment_path, blank=True, validators=[validate_file_size])


