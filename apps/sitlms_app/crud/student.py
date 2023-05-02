from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from apps.sitlms_app.models import Students, Students_Auth
from apps.sitlms_app.forms import StudentForm
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
import string
import secrets
from .sit_admin import generate_random_string
from django.contrib.auth.models import User
from django.contrib import messages

def pass_gen():

    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation

    pwd_length = 7
    alphabet = letters + digits

    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))

    pwd += secrets.choice(special_chars)

    return pwd

""" This validate function checks if an existing username is present in the table"""
def validate(username):
            if username in Students.objects.values_list('username', flat=True):
                suffix = 1
                new_username = username + str(suffix)
                while new_username in Students.objects.values_list('username', flat=True):
                    suffix +=1
                    new_username = username+str(suffix)
                return new_username
            else:
                return username


def student(request): 

    if request.method == "POST":
        form = StudentForm(request.POST)  
        if form.is_valid():
            try:              #completely fill-in na ng data si form, including username
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                username=request.POST['email']
                email=request.POST['email']
                password=generate_random_string(8)
                if User.objects.filter(email=email).exists():
                    messages.info(request, 'Email Already Used. Contact admin to edit profile instead.')
                    return redirect('admincreate')
                else:
                    user = User.objects.create_user(username=username, email = email, password=password, first_name=first_name, last_name=last_name, is_active=True,)
                    user.save()
                    middlename=request.POST['middlename']
                    birthdate=request.POST['birthdate']
                    program_id=request.POST['program_id']
                    student_no=request.POST['student_no']
                    employment_status=request.POST['employment_status']
                    student = Students_Auth(user=user, middlename=middlename, birthdate=birthdate, program_id=program_id, student_no=student_no, employment_status=employment_status)
                    student.save()
                    return redirect("/sit-admin/student/view")
            except Exception as e:
                print(str(e))
        else:
            print(form.errors)
    else:
        form = StudentForm()            #loads the student form with autofill on some fields

    return render(request, 'admin_module/add_student.html', {'form':form, })

def view_students(request):
    students = Students_Auth.objects.all()                           #access the model and show all the content
    return render(request, 'admin_module/view_students.html', {'students':students})  #passes the students as context to the show.html

def edit_student(request, id):
    student = Students_Auth.objects.get(id=id)     
    email_for_reset = student.user.email          #get the id of the student
    return render(request, 'admin_module/edit_student.html', {'student':student, 'email':email_for_reset})    #passes the student as context to the edit.html

def update_student(request, id):
    # JQBM: Ano difference ng update at edit na views?
    student = Students_Auth.objects.get(id=id)
    email_for_reset = student.user.email
    template = loader.get_template('admin_module/edit_student.html')
    context = {'student': student, 'email':email_for_reset}
    return HttpResponse(template.render(context, request))

def delete_student(request, id):
    student = Students_Auth.objects.get(id=id)
    # JQBM: Walang confirmation for delete?
    student.delete()
    return redirect("/sit-admin/student/view")
    
def update_record(request, id):
    program_id = request.POST['program_id']
    student_no = request.POST['student_no']
    email = request.POST['email']
    username = request.POST['email']
    firstname = request.POST['firstname']
    middlename = request.POST['middlename']
    lastname = request.POST['lastname']
    birthdate = request.POST['birthdate']
    convert_birthdate = parse_date(birthdate)
    employment_status = request.POST['employment_status']
    active_deactive = request.POST['active_deactive']
    access_type = request.POST['access_type']

    student = Students_Auth.objects.get(id=id)
    student.program_id = program_id
    student.student_no = student_no
    student.user.email = email
    student.user.username = username
    student.user.firstname = firstname
    student.middlename = middlename
    student.user.lastname = lastname
    student.birthdate = convert_birthdate
    student.employment_status = employment_status
    student.active_deactive = active_deactive
    student.access_type = access_type
    student.user.save()
    student.save()

    return redirect("/sit-admin/student/view")