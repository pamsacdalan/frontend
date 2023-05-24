from django import forms
from apps.sitlms_student.models import Activity_Submission

class ActivitySubmissionUploadForm(forms.ModelForm):
    activity_file = forms.FileField(widget=forms.ClearableFileInput())

    class Meta:
        model = Activity_Submission
        fields = ['activity_file']
