from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, time
from django.utils import timezone
# Create your models here.

active_inactive = (
    ('Active','Active'),
    ('Inactive','Inactive'),
)

access_code = (
    (0,0),
    (1,1),
    (2,2),
)

employment_status = (
    ('Deployed','Deployed'),
    ('Training','Training'),
)



class Students(models.Model):
    student_id = models.IntegerField(primary_key=True)
    program_id = models.IntegerField()
    student_no = models.IntegerField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    birthdate = models.DateField()
    employment_status = models.CharField(max_length=50, choices=employment_status, default='Deployed')
    active_deactive = models.CharField(max_length=50, choices=active_inactive, default="Active")
    access_type = models.IntegerField(choices = access_code, default=0)

    def str(self):
        return self.name

    class Meta:
        db_table = 'students'


class Instructor(models.Model):
    """
    Class for instructor fields
    """
    instructor_id =  models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password  = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    birthdate = models.DateField()
    active_deactive  = models.BooleanField(default=True)
    access_type = models.IntegerField(default=2)
    class Meta:
        db_table = 'instructor'

    def __str__(self):
        return self.username

class Program(models.Model):
    program_id= models.IntegerField(primary_key=True, unique=True)
    program_code = models.CharField(max_length=50)      #JAVAFS1, JAVAFS2
    program_title = models.CharField(max_length=50)     #Java Full Stack, ETL, MLE
    
    def str(self):
        return self.program_code
    def to_desc(self):
        return self.program_title


class Instructor_Auth(models.Model):
    """
    Class for instructor fields
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #username = models.CharField(max_length=255)
    #password  = models.CharField(max_length=255)
    # email
    #firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255,blank=True,null=True)
    #lastname = models.CharField(max_length=255)
    birthdate = models.DateField()
    # active_deactive  = models.BooleanField(default=True)
    access_type = models.IntegerField(default=3, validators=[MaxValueValidator(3), MinValueValidator(1)])

    

    def __str__(self):
        full_name = self.user.first_name + " " + self.user.last_name
        return full_name

class Course_Catalog(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_desc = models.CharField(max_length=100)
    course_title = models.CharField(max_length=50)

    def __str__(self):
        return self.course_title
    
class Course_Enrollment(models.Model):
    course_batch = models.CharField(max_length=10, primary_key=True, unique=True)
    course_id = models.ForeignKey(Course_Catalog, on_delete=models.CASCADE)
    instructor_id = models.ForeignKey(Instructor_Auth, on_delete=models.CASCADE)
    session_details = models.URLField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(default=time(0,0,0))
    end_time = models.TimeField(default=time(0,0,0))
    frequency = models.IntegerField(null=True)
    course_mode = models.IntegerField()

    def __str__(self):
        return self.course_batch

# Unified Auth Models
# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=255,blank=True,null=True)
    birthdate = models.DateField(null=True,blank=True)
    access_type = models.IntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])

    def get_absolute_url(self):
        return '/admin_module/list'
    
class Students_Auth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program_id = models.ForeignKey(Program, on_delete=models.CASCADE)
    student_no = models.CharField(max_length=7)
    #username = models.CharField(max_length=50)
    #password = models.CharField(max_length=50)
    #firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50,blank=True,null=True)
    #lastname = models.CharField(max_length=50)
    #email = models.EmailField(max_length=100)
    birthdate = models.DateField()
    employment_status = models.CharField(max_length=50, choices=employment_status, default='Deployed')
    active_deactive = models.CharField(max_length=50, choices=active_inactive, default="Active")
    access_type = models.IntegerField(default=2, validators=[MaxValueValidator(3), MinValueValidator(1)])

class Student_Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students_Auth, on_delete=models.CASCADE)
    course_batch = models.ForeignKey(Course_Enrollment, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='Ongoing')
    grades = models.CharField(max_length=3)
    date_enrolled = models.DateTimeField()

    def __str__(self):
        return self.enrollment_id
    

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    session_date = models.DateField(null= True, blank=True, auto_now_add=False, auto_now=False)
    start_time = models.TimeField(null= True, blank=True, auto_now_add=False, auto_now=False)
    end_time = models.TimeField(null= True, blank=True, auto_now_add=False, auto_now=False)
    course_batch = models.ForeignKey(Course_Enrollment, on_delete=models.CASCADE)
    # user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)


class Csv(models.Model):  
    file_name  = models.FileField(upload_to='files')
    uploaded = models.DateTimeField(auto_now=True)
    activated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"File id: {self.id}"
    

class Change_Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    course_batch = models.ForeignKey(Course_Enrollment, on_delete=models.CASCADE)
    old_start_date = models.DateField(null= True, blank=True, auto_now_add=False, auto_now=False)
    old_end_date = models.DateField(null= True, blank=True, auto_now_add=False, auto_now=False)
    old_start_time = models.TimeField(null= True, blank=True, auto_now_add=False, auto_now=False)
    old_end_time = models.TimeField(null= True, blank=True, auto_now_add=False, auto_now=False)
    new_start_date = models.DateField(null= True, blank=True, auto_now_add=False, auto_now=False)
    new_end_date = models.DateField(null= True, blank=True, auto_now_add=False, auto_now=False)
    new_start_time = models.TimeField(null= True, blank=True, auto_now_add=False, auto_now=False)
    new_end_time = models.TimeField(null= True, blank=True, auto_now_add=False, auto_now=False)
    old_frequency = models.IntegerField(null=True)
    new_frequency = models.IntegerField(null=True)
    request_date = models.DateTimeField(default=timezone.now)
    approval_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=255, default="Pending")

class Student_Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=10000, null=True)
    address = models.CharField(max_length=10000, null=True)
    user_contact_no = models.CharField(max_length=255, null=True)
    emergency_contact = models.CharField(max_length=255, null=True)
    emergency_contact_no = models.CharField(max_length=20, null=True)
    profile_pic = models.ImageField(upload_to='student_pic/', null=True)

    def str(self):
        return self.user.username

