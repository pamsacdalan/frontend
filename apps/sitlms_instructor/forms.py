from django import forms
from .widget import DateTimePickerInput,SplitDateTimeWidget,SplitDateTimeField
from apps.sitlms_instructor.models import Course_Activity


class ActivityForms(forms.Form):
      course_batch = forms.CharField(max_length=10)
      activity_title = forms.CharField()
      activity_desc= forms.CharField(widget=forms.Textarea)
      activity_attachment= forms.URLField(min_length=1, required=False)
      deadline= SplitDateTimeField()    
    # grading_percentage= forms.IntegerField()
      class Meta:
            model = Course_Activity
            fields = [
                    'course_batch',
                    'activity_title',
                    'activity_desc',
                    'activity_attachment',
                #   'start_date',
                    'deadline',
                    # 'grading_percentage'
            ]
   

