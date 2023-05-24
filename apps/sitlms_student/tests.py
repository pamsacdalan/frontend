from django.test import TestCase

# Create your tests here.
def student_edit_profile(request):
    
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    """ This function renders the student edit profile"""
    student_auth_details = Students_Auth.objects.get(user_id=user_id)
    student_profile = Student_Profile.objects.get(user_id=user_id)
    print(student_profile.profile_pic)
    
    #user_ids = student_auth_details.values_list('user_id')
    #student_details = User.objects.filter(id__in=user_ids).values('first_name', 'last_name', 'username', 'password')
    
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
    
    # print(type(student_details['birthdate']))
    
    
    context = {'student_details': student_details      
    }
    #if request.method == 'POST' or request.FILES['profile_pic']:
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

        # print("I am the file",request.FILES['profile_pic'])
        profile_pic = False

        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']

        # print(type(profile_pic), profile_pic)
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
        student_profile.bio = bio
        student_profile.address = address
        student_profile.user_contact_no = user_contact_no
        student_profile.emergency_contact = emergency_contact
        student_profile.emergency_contact_no = emergency_contact_no
         
        
        if profile_pic:
            student_profile.profile_pic = os.path.join('student_pic', profile_pic.name)
        

        student_auth_details.user.save()
        student_auth_details.save()
        student_profile.save()

        
        return redirect('/sit-student/student_profile')
    
    return render(request, 'student_module/edit_profile.html', context)