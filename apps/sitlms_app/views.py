from django.conf import settings
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth.forms import PasswordResetForm
from .forms import CsvModelForm
from .models import Csv, Change_Schedule, Schedule, Course_Enrollment
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
from apps.sitlms_app.crud.enrolled_course import string_to_date 
from datetime import datetime, date
from django.db.models import Q


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
    print('Something went wrong')
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




def change_schedule_approval(request):
    
    template = loader.get_template('admin_module/instructor_change_schedule_approval.html')
    change_schedule_list = Change_Schedule.objects.filter(status='Pending').values()
    # print(change_schedule_list)
    context = {'change_schedule_list':change_schedule_list
                }
    return HttpResponse(template.render(context,request))



def approve_change_schedule(request, id):

    # For changing status from pending to approved
    change_schedule = Change_Schedule.objects.filter(id=id)
    change_schedule.update(status="Approved", approval_date = datetime.now())


    # For changing schedules in course enrollment table
    change_schedule_all = Change_Schedule.objects.get(id=id)
    enrolled_course = Course_Enrollment.objects.filter(course_batch=change_schedule_all.course_batch) #ex: Python101
    enrolled_course.update(
        start_date = change_schedule_all.new_start_date,
        end_date = change_schedule_all.new_end_date,
        start_time = change_schedule_all.new_start_time,
        end_time = change_schedule_all.new_end_time,
        frequency = change_schedule_all.new_frequency
    )
    
    #DELETES THE RECORD IN SCHEDULED TABLE, THEN SAVE ANOTHER RECORD
    enrolled_course_all = Course_Enrollment.objects.get(course_batch=change_schedule_all.course_batch)
    scheduled_course = list(Schedule.objects.filter(**{'course_batch':enrolled_course_all.course_batch}).values()) #gets each entry of the argument id from schedule table


    frequency = enrolled_course_all.frequency
    start_date = enrolled_course_all.start_date
    end_date = enrolled_course_all.end_date
    start_time = enrolled_course_all.start_time
    end_time = enrolled_course_all.end_time
    course_batch = enrolled_course_all.course_batch

    print(type(start_date), type(end_date), str(start_time), str(end_time))


    for record in scheduled_course:
        deleted_scheduled_course = Schedule.objects.get(schedule_id=record['schedule_id'])
        deleted_scheduled_course.delete()
    
    string_to_date(str(frequency), str(start_date), str(end_date), str(start_time)[:5], str(end_time)[:5], course_batch)

    return redirect('/sit-admin/course_enrollment/change_schedule/')


def reject_change_schedule(request, id):

    change_schedule = Change_Schedule.objects.filter(id=id)
    change_schedule.update(status="Rejected", approval_date = datetime.now())

    return redirect('/sit-admin/course_enrollment/change_schedule/')

def view_history(request):
    
    #change_schedule_list = Change_Schedule.objects.filter(status='Pending').values()
    template = loader.get_template('admin_module/instructor_history_change_schedule_requests.html')
    history_list = Change_Schedule.objects.filter(Q(status='Approved')| Q(status='Rejected') ).values()
    print(history_list)
    context = {'change_schedule_list':history_list}

    return HttpResponse(template.render(context,request))
 