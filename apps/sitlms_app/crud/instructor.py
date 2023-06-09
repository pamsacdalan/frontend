from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from apps.sitlms_app.models import Instructor, Instructor_Auth, Student_Profile
from django.shortcuts import render, redirect
from django.urls import reverse
from .sit_admin import generate_random_string
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_app.crud.access_test import is_admin, send_initial_password_resest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Value, CharField

# CRUD for Instructor
@user_passes_test(is_admin)
def instructor(request):
    return render(request,'admin_module/instructor.html')

@user_passes_test(is_admin)
def add_instructor(request):
    template = loader.get_template('admin_module/add_instructor.html')
    return HttpResponse(template.render({},request))

@user_passes_test(is_admin)
def view_instructors(request):
    template = loader.get_template('admin_module/view_instructor.html')
    instructor_list = Instructor_Auth.objects.all().annotate(biography=Value("",output_field=CharField()),
                                                    address=Value("",output_field=CharField()),
                                                    contact_number=Value("",output_field=CharField()),
                                                    contact_person=Value("",output_field=CharField()),
                                                    emergency_contact_num=Value("",output_field=CharField()),)
    # context = {'instructor_list':instructor_list}
    user_id_list = Student_Profile.objects.values_list("user_id", flat=True)
    for x in instructor_list:
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
    paginator = Paginator(instructor_list, items_per_page)
    try:
            instructor_page = paginator.page(page)
    except PageNotAnInteger:
            instructor_page = paginator.page(1)
    except EmptyPage:
            instructor_page = paginator.page(paginator.num_pages)
                
    context = {'instructor_page':instructor_page, 'instructor_list': instructor_list}
    return HttpResponse(template.render(context,request))
    
    
    # return HttpResponse(template.render(context,request))

@user_passes_test(is_admin)
def add_instructor_info(request):

    if request.method == "POST":
        username  = request.POST['username']
        password = generate_random_string(8)
        firstname  = request.POST['firstname']
        middlename  = request.POST['middlename'] if request.POST['middlename'] else None
        lastname  = request.POST['lastname']
        birthdate  = request.POST['birthdate']
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Email Already Used. Contact admin to edit profile instead.')
            return redirect('add_instructor')
        user = User.objects.create_user(username=username, email = username, password=password, first_name=firstname, last_name=lastname, is_active=True,)
        user.save()
        instructors = Instructor_Auth(user=user,middlename=middlename,birthdate=birthdate)
        instructors.save()
        send_initial_password_resest(request, user)
        messages.success(request, "Successfully Added")
        return redirect('view_instructors')

    return HttpResponseRedirect(reverse('add_instructor'))

@user_passes_test(is_admin)
def delete_instructor(request,id):
    instructor = Instructor_Auth.objects.get(id=id)
 
    if request.method == "POST":
        instructor.delete()
        messages.success(request, "Successfully Deleted")
        return redirect('view_instructors')
 
    return render(request, "admin_module/view_instructor.html")

@user_passes_test(is_admin)
def edit_instructor(request,id):
    instructor = Instructor_Auth.objects.get(id=id)
    context = {'instructor':instructor}

    if request.method == "POST":

        username  = request.POST['username']
        firstname  = request.POST['firstname']
        middlename  = request.POST['middlename'] if request.POST['middlename'] else None
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
        messages.success(request, "Successfully Edited")
        return redirect('view_instructors')
    
    return render(request, "admin_module/edit_instructor.html", context)