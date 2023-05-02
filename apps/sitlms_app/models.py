from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
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

class Course_Catalog(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_desc = models.CharField(max_length=100)
    course_title = models.CharField(max_length=50)

    def __str__(self):
        return self.course_title
    
class Course_Enrollment(models.Model):
    course_batch = models.CharField(max_length=10, primary_key=True, unique=True)
    course_id = models.ForeignKey(Course_Catalog, on_delete=models.CASCADE)
    instructor_id = models.IntegerField()
    session_details = models.URLField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    course_mode = models.IntegerField()

    def __str__(self):
        return self.course_batch

# Unified Auth Models
# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=255,blank=True)
    birthdate = models.DateField(null=True,blank=True)
    access_type = models.IntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])

    def get_absolute_url(self):
        return '/admin_module/list'
    
class Students_Auth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program_id = models.IntegerField()
    student_no = models.CharField(max_length=7)
    #username = models.CharField(max_length=50)
    #password = models.CharField(max_length=50)
    #firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50)
    #lastname = models.CharField(max_length=50)
    #email = models.EmailField(max_length=100)
    birthdate = models.DateField()
    employment_status = models.CharField(max_length=50, choices=employment_status, default='Deployed')
    active_deactive = models.CharField(max_length=50, choices=active_inactive, default="Active")
    access_type = models.IntegerField(default=2, validators=[MaxValueValidator(3), MinValueValidator(1)])

class Instructor_Auth(models.Model):
    """
    Class for instructor fields
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #username = models.CharField(max_length=255)
    #password  = models.CharField(max_length=255)
    # email
    #firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255)
    #lastname = models.CharField(max_length=255)
    birthdate = models.DateField()
    # active_deactive  = models.BooleanField(default=True)
    access_type = models.IntegerField(default=3, validators=[MaxValueValidator(3), MinValueValidator(1)])