from django.conf import settings
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth.forms import PasswordResetForm
from apps.sitlms_app.crud.student import view_students
from .forms import CsvModelForm
from .models import Csv, Change_Schedule, Schedule, Course_Enrollment, Instructor_Auth, Student_Profile, SubmitIssue, Notification
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
from django.contrib.auth import get_user_model
import pandas as pd




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
    elif hasattr(request.user,'students_auth'):
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
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id
    """ This function renders the admin module dashboard """
    
    # return render(request, 'admin_module/dashboard.html')
    # Instructor
    instructor_list = Instructor_Auth.objects.all()
    # sum = Instructor_Auth.objects.all().aggregate(Sum('user_id')).values
    context = {'instructor_list':instructor_list}
    # return HttpResponse(template.render(context,request))
    issues = SubmitIssue.objects.all().values()
    count_issues = issues.filter(status=0).count()
    notifs =Notification.objects.filter(is_read=False, recipient_id=user_id).values()
    count_notifs = notifs.count()
    context = {
        'issues':issues,
        'alerts':count_issues,
        'notifs': notifs,
        'count_notifs':count_notifs     
    }

    return render(request, 'admin_module/dashboard.html',context)






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
                if i==0 or i==1:
                    pass
                
                else:     
                    # row = "".join(row)
                    # row = row.replace(";", " ")
                    # row = row.split()
                    try:
                        print(row[0])
                        print(row[1])
                        print(row[2])
                        username = row[3]
                        program_id = Program.objects.get(program_id=row[1])
                        user = User.objects.create_user(username=username, email = row[3], password=generate_random_string(8), first_name=row[4], last_name=row[6], is_active=True,)
                        student = Students_Auth(user=user, middlename=row[5], birthdate=row[7], program_id=program_id, student_no=row[2], employment_status=row[8])
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
      
    if request.method == "POST":
        if 'prog_list' in request.POST:
            prog_id = request.POST['prog_list']
            SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
            df = pd.read_csv(os.path.join(SITE_ROOT,'cv_template/sample_csv.csv'))
            path = os.path.join(SITE_ROOT,'cv_template/')
            split = prog_id.split("-")
            val = split[0]
            df.loc[0,'program_id'] = val
            df.to_csv(path+'sample_csv.csv', index=False)
            #FOR DEBUGGING
            # print(df)
            # print(prog_id)
            # print(split[0])
            #SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
            filename = open(os.path.join(SITE_ROOT,'cv_template/sample_csv.csv'),'r').read()
            response = HttpResponse(filename)
            response['Content-Disposition'] = 'attachment;filename=sample_csv.csv'
            return response
        else:
            prog_id = False
            messages.error(request,'Please select a Program!')
            return view_students(request)
        

@user_passes_test(is_admin)
def csv_instruction(request):
    #CSV Template Instruction
    return render(request, 'admin_module/csv_instruction.html')



def reset_pw_request_success(request):
    
    """ This function renders the success page for password reset request """
    
    return render(request, 'registration/reset_pw_email.html')




def change_schedule_approval(request):
    
    template = loader.get_template('admin_module/instructor_change_schedule_approval.html')
    change_schedule_list = Change_Schedule.objects.filter(status='Pending').values()
    

    for value in range(len(change_schedule_list)):

        course_batch = change_schedule_list[value]['course_batch_id']
        instructor_id =  Course_Enrollment.objects.values('instructor_id').get(course_batch=course_batch)
        instructor = Instructor_Auth.objects.get(id=instructor_id['instructor_id'])
        # print(instructor)
        # print(instructor_id['instructor_id'])

        change_schedule_list[value]['instructor_id'] = instructor
        # print(change_schedule_list[value])

    
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

    # print(type(start_date), type(end_date), str(start_time), str(end_time))


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
    # print(history_list)
    context = {'change_schedule_list':history_list}

    return HttpResponse(template.render(context,request))




def edit_profile(request):
    
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    """ This function renders the student edit profile"""
    admin_auth_details = User.objects.get(id=user_id)
    admin_middlename_obj = Admin.objects.get(user_id=user_id)
    # print(Admin.objects.get(user_id=user_id).middle_name)
    if user_id in Student_Profile.objects.values_list('user_id', flat=True):
        student_profile = Student_Profile.objects.get(user_id=user_id)
        student_profile.profile_pic = str(student_profile.profile_pic).replace("\\","/")
        student_profile.save()
        
    
        
        admin_details ={ 'first_name':admin_auth_details.first_name,
                         'middle_name': admin_middlename_obj.middle_name, 
                        'last_name':admin_auth_details.last_name,
                        'bio':student_profile.bio,
                        'address':student_profile.address,
                        'user_contact_no':student_profile.user_contact_no,
                        'emergency_contact':student_profile.emergency_contact,
                        'emergency_contact_no':student_profile.emergency_contact_no,
                        'profile_pic':student_profile.profile_pic,
                        'email': admin_auth_details.email
                    }   
    
    else:
        admin_details ={ 'first_name':admin_auth_details.first_name,
                         'middle_name': admin_middlename_obj.middle_name,
                        'last_name':admin_auth_details.last_name,
                        'bio':"",
                        'address':"",
                        'user_contact_no':"",
                        'emergency_contact':"",
                        'emergency_contact_no':"",
                        'profile_pic':"",
                        'email': admin_auth_details.email
                    }   
    
    
    
    context = {'admin_details': admin_details      
    }

    if request.method == 'POST':
        first_name = request.POST['first_name']
        middle_name = request.POST['middle_name']
        last_name = request.POST['last_name']
        bio = request.POST['bio']
        address = request.POST['address']
        user_contact_no = request.POST['user_contact_no']
        emergency_contact = request.POST['emergency_contact']
        emergency_contact_no = request.POST['emergency_contact_no']
         
         
        profile_pic = False

        if 'profile_pic' in request.FILES:
            profile_picture = request.FILES['profile_pic']
            profile_pic = f"{user_id}{os.path.splitext(profile_picture.name)[1]}"


        if profile_pic:
            static_dirs = settings.STATICFILES_DIRS  # Get the STATICFILES_DIRS list from Django settings
            student_pic_folder = os.path.join(static_dirs[0], 'admin_pic')
            os.makedirs(student_pic_folder, exist_ok=True)

            file_path = os.path.join(student_pic_folder, profile_pic)
            
            with open(file_path, 'wb') as destination:
                for chunks in profile_picture.chunks():
                    destination.write(chunks)

            
          

        admin_auth_details.first_name = first_name
        admin_middlename_obj.middle_name = middle_name
        admin_middlename_obj.save()

        admin_auth_details.last_name = last_name

        if user_id in Student_Profile.objects.values_list('user_id', flat=True):
            student_profile.bio = bio
            student_profile.address = address
            student_profile.user_contact_no = user_contact_no
            student_profile.emergency_contact = emergency_contact
            student_profile.emergency_contact_no = emergency_contact_no

            #enters here if may record sa student_profile, used only for updating profile pic
            if profile_pic:
                student_profile.profile_pic = str(os.path.join(settings.STATIC_URL, 'admin_pic', profile_pic)).replace("\\","/")

            

        else:
            #enters here, no record yet on student profile, 

            if profile_pic:
                student_profile = Student_Profile(
                bio = bio,
                address = address,
                user_contact_no = user_contact_no,
                emergency_contact = emergency_contact,
                emergency_contact_no = emergency_contact_no,
                user_id=user_id,
                profile_pic=str(os.path.join(settings.STATIC_URL, 'admin_pic', profile_pic)).replace("\\","/"))
            else:
                student_profile = Student_Profile(
                bio = bio,
                address = address,
                user_contact_no = user_contact_no,
                emergency_contact = emergency_contact,
                emergency_contact_no = emergency_contact_no,
                user_id=user_id,
                profile_pic=os.path.join(settings.STATIC_URL, 'student/assets/imgs/profile.png'))


        
        student_profile.save()
        admin_auth_details.save()
        

        
        return redirect('/sit-admin/dashboard/')
    
    return render(request, 'admin_module/edit_profile.html', context)

def view_issues(request):
    """Details to display issues page"""
    
    instructors = SubmitIssue.objects.filter(sender_access_type=1, status=0)
    students = SubmitIssue.objects.filter(sender_access_type=2, status=0)
    done = SubmitIssue.objects.filter(status = 1)
    context = {
        'students':students,
        'instructors':instructors,
        'done':done,
    }
    #DEBUG
    # print(instructors)
    # print("---------------------")
    # print(students)
    return render(request,'admin_module/view_issues.html', context)

def view_issues_details(request, id):
    """Details to display clickable issues notif"""
    issues = SubmitIssue.objects.get(id=id)

    context = {
        'issue':issues,
    }

    if request.method == 'POST':
        issues.status = 1
        issues.save(update_fields=['status'])
        return redirect('/sit-admin/dashboard')
    return render(request,'admin_module/issue_details.html', context)


def view_notifs(request):
    """Details to display issues page"""
    notifications = Notification.objects.all().values()
    context = {
        'notifications': notifications
    }
    return render(request,'admin_module/view_notifs.html', context)


def read_notif(request, id):
    notifications = Notification.objects.get(id=id)
    notifications.is_read = True
    notifications.save()

    return redirect("change_schedule")
     



