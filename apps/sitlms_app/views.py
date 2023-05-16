from django.conf import settings
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth.forms import PasswordResetForm
from .forms import CsvModelForm
from .models import Csv
import csv 
from django.contrib.auth.models import User 
from .models import Students_Auth, Program
import string
import random
import os
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_app.models import Admin
from django.core.exceptions import PermissionDenied


# Custom test function that checks if the user is an admin
def is_admin(user):
    try:
        access_type = Admin.objects.values_list('access_type', flat=True).get(user=user.id)
        # print(access_type)
        if access_type == 1:
            return True
        return False

    except Exception as e:
        raise PermissionDenied
        # return False


def home(request):
    
    """ This function renders the home page """
    messages.success(request,'You have successfully logged in.')
    if hasattr(request.user,'admin'):
        return redirect('sit_admin_dashboard')
    elif hasattr(request.user,'instructor_auth'):
        return redirect('instructor')
    elif hasattr(request.user,'student_auth'):
        return redirect('student_profile')
    # print('Something went wrong')
    return render(request, 'landing.html')
    # return render(request, 'registration/login.html')
    # return render(request, 'admin_module/index.html')


# @user_passes_test(is_admin)
# def admin_index(request):
    
#     """ This function renders the home page """
    
#     return render(request, 'admin_module/index.html')

@user_passes_test(is_admin)
def dashboard(request):
    
    """ This function renders the admin module dashboard """
    
    return render(request, 'admin_module/dashboard.html')


def password_reset(request, data):
    if request.method == 'POST':
        form = PasswordResetForm(data)
        if form.is_valid():
            form.save(request=data)
        return render(request, 'registration/password_reset_done.html')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# @user_passes_test(is_admin)
# def confirm_delete(request):
#     return render(request,'delete_student.html')

@user_passes_test(is_admin)
def view_csv(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save()
        with open(obj.file_name.path, 'r') as f:
            #Read CSV
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                #Remove header
                if i==0:
                    pass
                else:     
                    # row = "".join(row)
                    # row = row.replace(";", " ")
                    # row = row.split()
                    try:
                        username = row[3]
                        program_id = Program.objects.get(program_id=row[1])
                        user = User.objects.create_user(username=username, email = row[3], password=generate_random_string(8), first_name=row[4], last_name=row[6], is_active=True,)
                        student = Students_Auth(user=user, middlename=row[5], birthdate=row[7], program_id=program_id, student_no=row[0], employment_status=row[8])
                        student.save()
                        print(row)
                        print(type(row))
                    
                        obj.activated = True
                        obj.save()
                    except ValidationError:
                        messages.error(request,'Use a YYYY-MM-DD Format for the date!')
                    except TypeError:
                        messages.error(request, 'Invalid input')
                    except IntegrityError:
                        messages.error(request, 'Email already exists!')
            return redirect("/sit-admin/student/view")
    return render(request,'admin_module/import_csv.html',{'form':form})

@user_passes_test(is_admin)
def downloadfile(request):
    #Download CSV Template
    SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
    filename = open(os.path.join(SITE_ROOT,'cv_template/sample_csv.csv'),'r').read()
    response = HttpResponse(filename)
    response['Content-Disposition'] = 'attachment;filename=sample_csv.csv'
    return response

@user_passes_test(is_admin)
def csv_instruction(request):
    #CSV Template Instruction
    return render(request, 'admin_module/csv_instruction.html')


def student_profile(request):
    
    """ This function renders the student page """
    
    return render(request, 'student_module/student.html')

def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')


def student_edit_profile(request):
    
    """ This function renders the student edit profile"""
    
    return render(request, 'student_module/edit_profile.html')

def reset_pw_request_success(request):
    
    """ This function renders the success page for password reset request """
    
    return render(request, 'registration/reset_pw_email.html')