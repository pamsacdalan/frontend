from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password, password_changed, password_validators_help_texts, password_validators_help_text_html
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.forms import  PasswordChangeForm

from apps.sitlms_app.models import Admin, Instructor, Course_Catalog, Course_Enrollment, Students_Auth,Instructor_Auth
from apps.sitlms_app.forms import AdminCreateForm, AdminUpdateForm,UserUpdateForm

from pathlib import Path

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.dateparse import parse_date
import string
import secrets
import random
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_app.crud.access_test import is_admin, send_initial_password_resest
from django.contrib.auth.mixins import UserPassesTestMixin


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class AdminList(ListView):
   model = Admin
   template_name='admin_module/admin_list.html'
   
   def test_func(self):
       if not is_admin(self.request.user):
           return is_admin(self.request.user)
       return is_admin(self.request.user)

# CRUD - (C)reate
class AdminCreate(CreateView):
   model = Admin
   template_name = 'admin_module/admin_create_form.html'
   form_class = AdminCreateForm
   
   def test_func(self):
       if not is_admin(self.request.user):
           return is_admin(self.request.user)
       return is_admin(self.request.user)


@user_passes_test(is_admin)
def sitadmin_register(request):
    if request.method == 'POST':
        form = AdminCreateForm(request.POST)
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username=request.POST['email_address']
        email=request.POST['email_address']
        password=generate_random_string(8)
        try:
            #validate_password(password)
            pass
        except:
            messages.info(request, 'Your password is not strong enough.' )
            #messages.info(request, password_validators_help_text_html())
            #print(password_validators_help_text_html())
            return redirect('admincreate')
        password2=password
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Used. Contact admin to edit profile instead.')
                return redirect('admincreate')
            else:
                user = User.objects.create_user(username=username, email = email, password=password, first_name=first_name, last_name=last_name, is_active=True, is_staff=True, is_superuser=True)
                user.save()
                middle_name=request.POST['middle_name'] if request.POST['middle_name'] else None
                birthdate=request.POST['birthdate']
                sitadmin = Admin(user=user, middle_name=middle_name, birthdate=birthdate)
                sitadmin.save()
                send_initial_password_resest(request, user)
                return redirect('sit_admin_dashboard')
        else:
            messages.info(request, 'Password Not The Same')
            return redirect('admincreate')
    else:
        form = AdminCreateForm()
        return render(request, 'admin_module/admin_create_form.html', {"form": form}) 


@user_passes_test(is_admin)
def sitadmin_update(request, id):
    if request.method == 'POST':
        sitadmin_model = Admin.objects.get(id=id)
        user_model = User.objects.get(id=sitadmin_model.user.id)
        form1 = UserUpdateForm(request.POST, instance=user_model)
        form2 = AdminUpdateForm(request.POST, instance=sitadmin_model)
        email_for_reset = user_model.email
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            user_model.username = form1.cleaned_data['email']
            user_model.save()
            messages.success(request, "Successfully Edited")
            return redirect('adminlist')
        else:
            messages.info(request, 'Form submission not valid.')
            return render(request,'admin_module/admin_update_form.html',{'form1': form_user_admin, 'form2':form_admin, 'email':email_for_reset})
    else: 
        sitadmin_model = Admin.objects.get(id=id)
        form_user_admin = AdminUpdateForm(instance=sitadmin_model)
        user_model = User.objects.get(id=sitadmin_model.user.id)
        form_admin = UserUpdateForm(instance=user_model)
        email_for_reset = user_model.email
        return render(request,'admin_module/admin_update_form.html',{'form1': form_user_admin, 'form2':form_admin, 'email':email_for_reset})

# CRUD - (D)elete
class AdminDelete(DeleteView):
    model = Admin
    template_name = 'admin_module/admin_delete_form.html'
    success_url = '/sit-admin/sit-admin/list'
    
    def test_func(self):
        if not is_admin(self.request.user):
            return is_admin(self.request.user)
        return is_admin(self.request.user)

