from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth.forms import PasswordResetForm

def home(request):
    
    """ This function renders the home page """
    
    return render(request, 'home.html')
    # return render(request, 'registration/login.html')
    # return render(request, 'admin_module/index.html')

def admin_index(request):
    
    """ This function renders the home page """
    
    return render(request, 'admin_module/index.html')

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



def student_profile(request):
    
    """ This function renders the admin module dashboard """
    
    return render(request, 'student_module/student.html')

def student_course_details(request):
    
    """ This function renders the admin module dashboard """
    
    return render(request, 'student_module/courses_details.html')