from django.contrib import admin
from .models import Admin, Students_Auth, Instructor_Auth, Csv

# Register your models here.
admin.site.register(Admin)
admin.site.register(Students_Auth)
admin.site.register(Instructor_Auth)

admin.site.register(Csv)