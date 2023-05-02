from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from apps.sitlms_app.models import Instructor, Instructor_Auth
from django.shortcuts import render, redirect
from django.urls import reverse
from .sit_admin import generate_random_string
from django.contrib.auth.models import User
from django.contrib import messages


# CRUD for Instructor

def instructor(request):
    return render(request,'admin_module/instructor.html')


def add_instructor(request):
    template = loader.get_template('admin_module/add_instructor.html')
    return HttpResponse(template.render({},request))

def view_instructors(request):
    template = loader.get_template('admin_module/view_instructor.html')
    instructor_list = Instructor_Auth.objects.all()
    context = {'instructor_list':instructor_list}
    return HttpResponse(template.render(context,request))

def add_instructor_info(request):

    if request.method == "POST":
        username  = request.POST['username']
        password = generate_random_string(8)
        firstname  = request.POST['firstname']
        middlename  = request.POST['middlename']
        lastname  = request.POST['lastname']
        birthdate  = request.POST['birthdate']
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Email Already Used. Contact admin to edit profile instead.')
            return redirect('add_instructor')
        user = User.objects.create_user(username=username, email = username, password=password, first_name=firstname, last_name=lastname, is_active=True,)
        user.save()
        instructors = Instructor_Auth(user=user,middlename=middlename,birthdate=birthdate)
        instructors.save()
        return redirect('view_instructors')

    return HttpResponseRedirect(reverse('add_instructor'))


def delete_instructor(request,id):
    instructor = Instructor_Auth.objects.get(id=id)
 
    if request.method == "POST":
        instructor.delete()
        return redirect('view_instructors')
 
    return render(request, "admin_module/delete_instructor.html")


def edit_instructor(request,id):
    instructor = Instructor_Auth.objects.get(id=id)
    context = {'instructor':instructor}

    if request.method == "POST":

        username  = request.POST['username']
        firstname  = request.POST['firstname']
        middlename  = request.POST['middlename']
        lastname  = request.POST['lastname']
        birthdate  = request.POST['birthdate']
  
        instructor.user.username = username
        instructor.user.email = username
        instructor.user.first_name = firstname
        instructor.middlename = middlename
        instructor.user.last_name = lastname
        instructor.birthdate = birthdate
        instructor.user.save()

        #instructor.save(update_fields=['username','password','firstname','middlename','lastname','birthdate'])
        instructor.save()

        return redirect('view_instructors')
    
    return render(request, "admin_module/edit_instructor.html", context)