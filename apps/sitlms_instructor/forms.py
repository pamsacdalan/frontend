from django import forms
from .widget import DateTimePickerInput,SplitDateTimeWidget,SplitDateTimeField
from apps.sitlms_instructor.models import Course_Activity


class ActivityForms(forms.Form):
      course_batch = forms.CharField(max_length=10)
      activity_title = forms.CharField()
      activity_desc= forms.CharField(widget=forms.Textarea)
      deadline= SplitDateTimeField()
      activity_attachment = forms.FileField(required=False)    
      scores = forms.IntegerField(min_value=1)
      percentage = forms.DecimalField(max_digits=5, decimal_places=2,max_value=100)
   

