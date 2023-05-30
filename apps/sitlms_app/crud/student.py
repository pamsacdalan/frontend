from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from apps.sitlms_app.models import Students, Students_Auth, Program, Student_Profile
from apps.sitlms_app.forms import StudentForm
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
import string
import secrets
from .sit_admin import generate_random_string
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_app.crud.access_test import is_admin, send_initial_password_resest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Value, CharField

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


@user_passes_test(is_admin)
def student(request): 

    program = Program.objects.all().values('program_code')
    program_list = []
    for i in range(len(program)):
         program_list.append(program[i]['program_code'])
    program_list.sort()

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
                    return redirect('/sit-admin/student')
                else:
                    user = User.objects.create_user(username=username, email = email, password=password, first_name=first_name, last_name=last_name, is_active=True,)
                    user.save()
                    middlename=request.POST['middlename'] if request.POST['middlename'] else None
                    birthdate=request.POST['birthdate']
                    program = Program.objects.values('program_id').get(program_code=request.POST['program_code'])
                    program_id = Program.objects.get(program_id=program['program_id'])
                    student_no=request.POST['student_no']
                    employment_status=request.POST['employment_status']
                    student = Students_Auth(user=user, middlename=middlename, birthdate=birthdate, program_id=program_id, student_no=student_no, employment_status=employment_status)
                    student.save()
                    messages.success(request, "Successfully Added")
                    send_initial_password_resest(request, user)
                    return redirect("/sit-admin/student/view")
            except Exception as e:
                print(str(e))
        else:
            print(form.errors)
    else:
        form = StudentForm()            #loads the student form with autofill on some fields


    return render(request, 'admin_module/add_student.html', {'form':form, 'program_list' : program_list})


@user_passes_test(is_admin)
def view_students(request):
    template = loader.get_template('admin_module/view_students.html')
    students = Students_Auth.objects.all().annotate(biography=Value("",output_field=CharField()),
                                                    address=Value("",output_field=CharField()),
                                                    contact_number=Value("",output_field=CharField()),
                                                    contact_person=Value("",output_field=CharField()),
                                                    emergency_contact_num=Value("",output_field=CharField()),)                           #access the model and show all the content
    """Details for drop down(CSV Template) selection"""
    list_of_programs = Program.objects.all().values().order_by('program_id')

    user_id_list = Student_Profile.objects.values_list("user_id", flat=True)
    for x in students:
        if x.user_id in user_id_list:
            print(x.user_id,Student_Profile.objects.values("bio").get(user_id=x.user_id)['bio'])
            x.biography = Student_Profile.objects.values("bio").get(user_id=x.user_id)['bio']
            x.address = Student_Profile.objects.values("address").get(user_id=x.user_id)['address']
            x.contact_number = Student_Profile.objects.values("user_contact_no").get(user_id=x.user_id)['user_contact_no']
            x.contact_person = Student_Profile.objects.values("emergency_contact").get(user_id=x.user_id)['emergency_contact']
            x.emergency_contact_num = Student_Profile.objects.values("emergency_contact_no").get(user_id=x.user_id)['emergency_contact_no']


    # for pagination
    page = request.GET.get('page', 1) # default page (default to first page)
        
    items_per_page = 10
    paginator = Paginator(students, items_per_page)
    try:
            students_page = paginator.page(page)
    except PageNotAnInteger:
            students_page = paginator.page(1)
    except EmptyPage:
            students_page = paginator.page(paginator.num_pages)
                
    context = {'students_page':students_page, 
               'students': students,
               'program_list':list_of_programs,}
    
    return HttpResponse(template.render(context,request))
    # return render(request, 'admin_module/view_students.html', {'students':students})  #passes the students as context to the show.html
    
    

@user_passes_test(is_admin)
def edit_student(request, id):
    student = Students_Auth.objects.get(id=id)   
    print(id)
    print(student.user_id)
    old_program = student.program_id.pk
    old_program = Program.objects.values('program_code').get(program_id=old_program)
    old_program = old_program['program_code']
    email_for_reset = student.user.email         #get the id of the student
    program = Program.objects.all().values('program_code')
    program_list = []
    for i in range(len(program)):
         program_list.append(program[i]['program_code'])
    program_list.sort()
    
    return render(request, 'admin_module/edit_student.html', {'student':student, 'email':email_for_reset, 'program_list':program_list,
                                                                'old_program':old_program})    #passes the student as context to the edit.html

@user_passes_test(is_admin)
def update_student(request, id):
    student = Students_Auth.objects.get(id=id)
    email_for_reset = student.user.email
    template = loader.get_template('admin_module/edit_student.html')
    context = {'student': student, 'email':email_for_reset}
    return HttpResponse(template.render(context, request))

@user_passes_test(is_admin)
def confirm_delete(request, id):
    student = Students_Auth.objects.get(id=id)
    return render(request, 'admin_module/view_students.html', {'student':student})

@user_passes_test(is_admin)
def delete_student(request, id):
    student = Students_Auth.objects.get(id=id)
    student.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("/sit-admin/student/view")


@user_passes_test(is_admin)  
def update_record(request, id):
    # program_id = request.POST['program_id']
    program = Program.objects.values('program_id').get(program_code=request.POST['program_code'])
    program_id = Program.objects.get(program_id=program['program_id'])
    student_no = request.POST['student_no']
    email = request.POST['email']
    username = request.POST['email']
    firstname = request.POST['firstname']
    middlename = request.POST['middlename'] if request.POST['middlename'] else None
    lastname = request.POST['lastname']
    birthdate = request.POST['birthdate']
    convert_birthdate = parse_date(birthdate)
    employment_status = request.POST['employment_status']
    #active_deactive = request.POST['active_deactive']
    active_deactive = True if request.POST['active_deactive'] == "True" else False
    #access_type = request.POST['access_type']

    student = Students_Auth.objects.get(id=id)
    if User.objects.filter(email=email).exists() and email != student.user.email:         
        messages.info(request, 'Email Already Used. Contact admin to edit profile instead.')
        return redirect("/sit-admin/student/view")
    # student_user = Students.objects.get(id=id)
    student.program_id = program_id
    student.student_no = student_no
    student.user.email = email
    student.user.username = username
    student.user.first_name = firstname
    student.middlename = middlename
    student.user.last_name = lastname
    student.birthdate = convert_birthdate
    student.employment_status = employment_status
    student.active_deactive = active_deactive
    #student.access_type = access_type
    student.user.save()
    student.save()

    messages.success(request, "Successfully Edited")
    return redirect("/sit-admin/student/view")