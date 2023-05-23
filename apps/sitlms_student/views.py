from django.shortcuts import render, redirect
from apps.sitlms_app.models import Students_Auth, Student_Enrollment, User, Student_Profile, Program
from django.conf import settings
import os
from django.contrib.auth import get_user_model

# Create your views here.

def create_student_photo_folder():
    """ This function will create the folder for student profile pic storage"""
    folder_path = os.path.join(settings.MEDIA_ROOT, 'student_photo')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def student_profile(request):    
    """ This function renders the student page """
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id
    student_auth_details = Students_Auth.objects.get(user_id=user_id)

    
    
    program_id = student_auth_details.program_id_id
    program = Program.objects.get(program_id=program_id)
    
    
    ongoing_count = Student_Enrollment.objects.filter(student_id=student_auth_details, status='Ongoing').count()
    completed_count = Student_Enrollment.objects.filter(student_id=student_auth_details, status='Completed').count()
    total_count = ongoing_count + completed_count


    
    ongoing_enrollments = Student_Enrollment.objects.filter(student_id=student_auth_details, status='Ongoing')
    for enrollment in ongoing_enrollments:
        print(f"Enrollment ID {enrollment.enrollment_id}, Course Batch: {enrollment.course_batch}")
        



    """ This function renders the student edit profile"""


    student_details ={ 'first_name':student_auth_details.user.first_name, 
                        'last_name':student_auth_details.user.last_name,
                        'program_title':program.program_title,
                        'ongoing_count':ongoing_count,
                        'completed_count':completed_count,
                        'total_count':total_count
                    }
    
    context  ={'student_details': student_details}
    
    
    return render(request, 'student_module/student.html', context)

def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')


def student_edit_profile(request):
    
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    """ This function renders the student edit profile"""
    student_auth_details = Students_Auth.objects.get(user_id=user_id)
    print(student_auth_details.user_id, user_id)
    if user_id in Student_Profile.objects.values_list('user_id', flat=True):
        student_profile = Student_Profile.objects.get(user_id=user_id)
        

        
        student_details ={ 'first_name':student_auth_details.user.first_name, 
                        'middlename':student_auth_details.middlename,
                        'last_name':student_auth_details.user.last_name,
                        'birthdate':student_auth_details.birthdate,
                        'bio':student_profile.bio,
                        'address':student_profile.address,
                        'user_contact_no':student_profile.user_contact_no,
                        'emergency_contact':student_profile.emergency_contact,
                        'emergency_contact_no':student_profile.emergency_contact_no,
                        'profile_pic':student_profile.profile_pic,
                        'email': student_auth_details.user.username,
                        'emp_no': student_auth_details.student_no
                    }   
    
    else:
        student_details ={ 'first_name':student_auth_details.user.first_name, 
                        'middlename':student_auth_details.middlename,
                        'last_name':student_auth_details.user.last_name,
                        'birthdate':student_auth_details.birthdate,
                        'bio':"",
                        'address':"",
                        'user_contact_no':"",
                        'emergency_contact':"",
                        'emergency_contact_no':"",
                        'profile_pic':"",
                        'email': student_auth_details.user.username,
                        'emp_no': student_auth_details.student_no
                    }   
    
    
    
    context = {'student_details': student_details      
    }

    if request.method == 'POST':
        first_name = request.POST['first_name']
        middlename = request.POST['middlename']
        last_name = request.POST['last_name']
        birthdate = request.POST['birthdate']
        bio = request.POST['bio']
        address = request.POST['address']
        user_contact_no = request.POST['user_contact_no']
        emergency_contact = request.POST['emergency_contact']
        emergency_contact_no = request.POST['emergency_contact_no']
         
         
         
        profile_pic = False 
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']

        if profile_pic:
            media_root = settings.MEDIA_ROOT
            student_pic_folder = os.path.join(media_root, 'student_pic')
            os.makedirs(student_pic_folder, exist_ok=True)
            print("hereeee")
            
            file_path = os.path.join(student_pic_folder, profile_pic.name)
            print(file_path, "THFDS")
            with open(file_path, 'wb') as destination:
                for chunks in profile_pic.chunks():
                    destination.write(chunks) 
          
          
          
          
          
          
          
            
        student_auth_details.user.first_name = first_name
        student_auth_details.middlename = middlename
        student_auth_details.user.last_name = last_name
        student_auth_details.birthdate = birthdate

        if user_id in Student_Profile.objects.values_list('user_id', flat=True):
            #student_profile = Student_Profile.objects.get(user_id=user_id)
            student_profile.bio = bio
            student_profile.address = address
            student_profile.user_contact_no = user_contact_no
            student_profile.emergency_contact = emergency_contact
            student_profile.emergency_contact_no = emergency_contact_no
            if profile_pic:
                student_profile.profile_pic = os.path.join('student_pic', profile_pic.name)
            

        else:
            student_profile = Student_Profile(
            bio = bio,
            address = address,
            user_contact_no = user_contact_no,
            emergency_contact = emergency_contact,
            emergency_contact_no = emergency_contact_no,
            user_id=user_id,
            profile_pic=profile_pic)

        
        
        
        student_profile.save()
        student_auth_details.user.save()
        student_auth_details.save()
        

        
        return redirect('/sit-student/student_profile')
    
    return render(request, 'student_module/edit_profile.html', context)