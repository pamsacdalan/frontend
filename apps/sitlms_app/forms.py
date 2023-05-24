from django import forms
from .models import Admin, Students, Course_Catalog, Course_Enrollment
from django.core.validators import int_list_validator, RegexValidator, MaxValueValidator
from datetime import datetime as datetime_jqbm, timezone, timedelta
import datetime
from django.db.models import Max
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from .models import Csv

'''
class StudentForm(forms.ModelForm):
    #this is added 01
    student_id = forms.CharField(label='Student ID', required=True)      


    class Meta:
        model = Students    #referred to class Students in models.py
        fields="__all__"
    
    #this is added 02
    def __init__(self, *args, **kwargs):
        today = datetime.date.today()
        year = today.year
        super().__init__(*args, **kwargs)
        if not self.instance.pk:

            if Students.objects.aggregate(Max('student_id'))['student_id__max'] == None:
                max_num = str(year) + '1'
                print(max_num)
            else:
                max_num = int(Students.objects.aggregate(Max('student_id'))['student_id__max']) +1
                print("not working")

            max_num = str(year) + str(max_num)[4:]
            self.fields['student_id'].initial = int(max_num)
'''

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['course_title','course_desc']
        model = Course_Catalog

from django.core.validators import int_list_validator, RegexValidator, MaxValueValidator
# Unified Auth Additional Forms
employment_status = (
    ('Deployed','Deployed'),
    ('Training','Training'),
)

# CRUD - Create
class AdminCreateForm(forms.Form):
    email_address = forms.EmailField(label='Email Address', widget=forms.EmailInput(attrs={'class':'form-control' , 'placeholder': 'Email address', "id": 'email_address'}))
    first_name = forms.CharField(min_length=1, max_length = 150, label='First Name', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'First Name', 'id': 'first_name', 'autocomplete': 'off'}), required=True)
    last_name = forms.CharField(min_length=1, max_length = 150, label='Last Name', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Last Name','id': 'last_name', 'autocomplete': 'off'}), required=True)
    middle_name = forms.CharField(min_length=2, max_length = 150, label='Middle Name', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Middle Name', 'id': 'middle_name', 'autocomplete': 'off'}), required=False)
    birthdate = forms.DateField(label='Birthdate', widget=forms.NumberInput(attrs={'class':'form-control','type': 'date', 'autocomplete': 'off'}), required=True,
                    validators=[
                            MaxValueValidator((datetime_jqbm.now(timezone(timedelta(hours=8))) - timedelta(days=1*365.25)).date(),
                                message="You must be at least 1 year old to apply."
                            )
                        ])
    
class AdminUpdateForm(forms.ModelForm):
    #form for updating Admins
    class Meta:
        model = Admin
        fields = ('middle_name', 'birthdate','access_type')

class UserUpdateForm(forms.ModelForm):
    #form for updating users
    class Meta:
        model = User
        fields = ('email','first_name', 'last_name','is_active')

class StudentForm(forms.Form):
    # program_id = forms.IntegerField(
    #     min_value=0,
    #     max_value=5,
    #     help_text='I think this should be a foreign key', 
    #     widget=forms.TextInput(attrs={'class':'form-control'})
    # )
    student_no = forms.CharField(max_length = 7, label='Employee ID', widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder': 'Email Address', 'autocomplete': 'off'}))
    first_name = forms.CharField(min_length=1, max_length = 150, label='first_name', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'First Name', 'id': 'first_name', 'autocomplete': 'off'}), required=True)
    middlename = forms.CharField(min_length=1, max_length = 150, label='middle_name', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Middle Name', 'id': 'middle_name', 'autocomplete': 'off'}), required=False)
    last_name = forms.CharField(min_length=1, max_length = 150, label='last_name', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Last Name','id': 'last_name', 'autocomplete': 'off'}), required=True)
    birthdate = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date', 'autocomplete': 'off'}), required=True,
                    validators=[
                            MaxValueValidator((datetime_jqbm.now(timezone(timedelta(hours=8))) - timedelta(days=1*365.25)).date(),
                                message="You must be at least 1 year old to apply."
                            )
                        ])
    employment_status = forms.CharField(label='gov_id', widget=forms.Select(attrs={'class':'form-control'}, choices=employment_status))
    
class CsvModelForm(forms.ModelForm):
    class Meta:
            model = Csv
            fields = ('file_name',)
            

