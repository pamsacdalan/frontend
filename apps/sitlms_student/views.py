from django.http import JsonResponse,HttpResponse
from django.shortcuts import redirect, render, redirect
from django.contrib.auth import get_user_model
from apps.sitlms_app.models import Course_Enrollment,  Students_Auth, Student_Enrollment, Student_Profile, Program, Course_Catalog,Instructor_Auth
from django.conf import settings
import os
from apps.sitlms_instructor.models import Activity_Comments, Course_Activity
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_student.forms import ActivitySubmissionUploadForm
from apps.sitlms_student.models import Activity_Submission
from django.utils import timezone
from datetime import datetime, timedelta, date as date2
from django.contrib.auth.models import User
from apps.sitlms_instructor.models import Course_Announcement
from operator import itemgetter
from calendar import monthcalendar
import calendar
from django.template.loader import render_to_string
from dateutil.relativedelta import relativedelta
# Create your views here.

def is_student(user):
    try:
        if hasattr(user,'students_auth'):
            return True
        raise PermissionDenied
    except Exception as e:
        raise PermissionDenied
    
def is_correct_student_cbatch_id(student, cbatch_id):
    try:
        # print(student)
        # print(Student_Enrollment.objects.filter(course_batch=cbatch_id).values('student_id'))
        # print('-')
        if Student_Enrollment.objects.filter(course_batch=cbatch_id, student_id=student).exists():
            pass
        else:
            return True
    except Exception as e:
        return True

@user_passes_test(is_student)   
def custom_403_2(request):
    # Pag pinasa ko with status=403, ayaw magload ng page :(
    # Dapat ganito: render(request, 'custom_403_1.html', status=403)
    return render(request, 'custom_403_2.html')



@user_passes_test(is_student)   
def student_view_course(request,id):
    if is_correct_student_cbatch_id(request.user.students_auth, id):
        return redirect("student-no-access")

    """This function displays the announcements, students, and additional information per course enrolled of the user"""

    course_batch = id
    user = request.user
    query = get_user_model().objects.filter(id=user.id)
    user_id = query.first().id

    """Details for Announcement Section"""
    announcement_details = Course_Announcement.objects.filter(course_batch = id).order_by("-date_posted").values()

    """Details for Course Info Section"""
    course_details = Course_Enrollment.objects.filter(course_batch=id).values()
    instructor_id = course_details[0]['instructor_id_id']
    instructor_details = Instructor_Auth.objects.get(id=instructor_id)
    instructor_name = f"{instructor_details.user.first_name} {instructor_details.user.last_name}"
    

  
    """Details for Classmates Section"""
    student_ids_enrolled = Student_Enrollment.objects.values_list('student_id').filter(course_batch=id)
    student_details = Students_Auth.objects.filter(id__in=student_ids_enrolled).exclude(user_id=user_id).values().order_by('id')
    program_ids = student_details.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values()

    count = len(student_details)
    complete_student_details = list()
    for x in range(count):
        for program in program_code:
            if student_details[x]['program_id_id'] == program['program_id']:
                name = Students_Auth.objects.get(id=student_details[x]['id'])
                student_full_name = {'full_name':f"{name.user.first_name} {name.user.last_name}", 'last_name':name.user.last_name}
                complete_student_details.append({**student_details[x], **program, **student_full_name})

    complete_student_details = sorted(complete_student_details, key=itemgetter('last_name'))
    enrolled_class = Student_Enrollment.objects.filter(course_batch=id)
    # print(enrolled_class)
    class_details = Course_Activity.objects.filter(course_batch=id)
    details_expanded = []
    for act in class_details:
        if Activity_Submission.objects.filter(course_activity=act,student_id=request.user.students_auth).exists():
            grade = Activity_Submission.objects.get(course_activity=act,student_id=request.user.students_auth).grade
            if grade is None:
                grade = 'Not graded yet'
        else:
            grade = 'Not handed in'
        details_expanded.append({'act':act,'grade':grade})
    context={
        'course_batch': course_batch,
        'announcement_details':announcement_details,
        'course_details':course_details,
        'classmate_details':complete_student_details,
        'instructor_name':instructor_name,
        'class':enrolled_class,
        'details':details_expanded,
        'id':id,
    }
    return render(request,'student_module/view_courses.html',context)

# def student_edit_profile(request):
    
#     """ This function renders the student edit profile"""
#     user = request.user
#     query = get_user_model().objects.filter(id=user.id)
#     user_id = query.first().id
#     student_id = Students_Auth.objects.get(user=user_id)
#     student_courses = Student_Enrollment.objects.filter(student_id=student_id).values()
#     enrolled_courses = Student_Enrollment.objects.filter(student_id=student_id).count
#     # print(student_courses)
      

#     context = {
#         'stud_id':student_id,
#         'course_count':enrolled_courses,
#         'course_enrolled_list':student_courses,

#                 }
#     return render(request, 'student_module/edit_profile.html',context)



    
    
    

"""no need na to since nasa loob na ng edit_student_profile yung pagccreate ng folder"""
# def create_student_photo_folder():
    
#     """ This function will create the folder for student profile pic storage"""
    
#     folder_path = os.path.join(settings.MEDIA_ROOT, 'student_photo')
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
        
@user_passes_test(is_student) 
def student_profile(request):    
    
    """ This function renders the student page """
    
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id
    student_auth_details = Students_Auth.objects.get(user_id=user_id)

    courses = Student_Enrollment.objects.filter(student_id=student_auth_details).values()
    enrolled_courses = Student_Enrollment.objects.filter(student_id=student_auth_details).count
    

    program_id = student_auth_details.program_id_id
    program = Program.objects.get(program_id=program_id)
    
    ongoing_count = Student_Enrollment.objects.filter(student_id=student_auth_details, status='Ongoing').count()
    completed_count = Student_Enrollment.objects.filter(student_id=student_auth_details, status='Completed').count()
    total_count = ongoing_count + completed_count
   
    
    ongoing_enrollments = Student_Enrollment.objects.filter(student_id=student_auth_details, status='Ongoing')
    for enrollment in ongoing_enrollments:
        print(f"Enrollment ID {enrollment.enrollment_id}, Course Batch: {enrollment.course_batch}")
        
    ## Schedule
    student_id = Students_Auth.objects.get(user=user_id)
    student_courses = Student_Enrollment.objects.filter(student_id=student_id).values()
    enrolled_courses = Student_Enrollment.objects.filter(student_id=student_id).count

    course_batch_list = student_courses.values_list('course_batch_id') # get course_batch
    # get course details using course_batch
    course_details = Course_Enrollment.objects.filter(course_batch__in=course_batch_list).values()
    course_details = [x for x in course_details] # convert query set to list
    for x in course_details:
        id = x['course_id_id']
        x['title'] = Course_Catalog.objects.get(course_id = id).course_desc # add course desc to dictionary
        
        start_date = x['start_date']
        end_date = x['end_date']

        delta = end_date - start_date  # returns timedelta
        days = []

        if x['frequency'] == 0:
            days.append(start_date)
        elif x['frequency'] == 1:
            for i in range(delta.days + 1):
                day = start_date  + timedelta(days=i)
                days.append(day)
        else:
            weeks = (end_date - start_date).days//7
            for i in range(0,weeks+1):
                days.append(start_date + timedelta(days=7*i))

        x['days'] = days

    student_details ={ 'first_name':student_auth_details.user.first_name, 
                        'last_name':student_auth_details.user.last_name,
                        'program_title':program.program_title,
                        'ongoing_count':ongoing_count,
                        'completed_count':completed_count,
                        'total_count':total_count,
                    }

    context  = {
        'student_details': student_details,
        'course_enrolled_list':courses,
        'stud_id':user_id,
        'course_count':enrolled_courses,
        'scheduled_course':course_details
               }
    
    # return render(request, 'student_module/student.html', context)

    # Get the current date from the URL parameters
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    date = datetime.strptime(date_str, '%Y-%m-%d')

    # Calculate the previous and next month values
    prev_month = date - relativedelta(months=1)
    next_month = date + relativedelta(months=1)

    prev_date = prev_month.replace(day=1).strftime('%Y-%m-%d')
    next_date = next_month.replace(day=1).strftime('%Y-%m-%d')

    # Generate the calendar data for the specified month
    cal = calendar.monthcalendar(date.year, date.month)

    # Get the current month's name and year
    month_name = date.strftime('%B')
    year = date.year

    # Prepare the calendar data with event information
    events = {
        5: ['Meeting 1', 'Meeting 2'],
        12: ['Appointment'],
        20: ['Conference'],
        25: ['Workshop', 'Training'],
    }

    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append((" ", []))
            else:
                events_for_day = events.get(day, [])
                week_data.append((day, events_for_day))
        calendar_data.append(week_data)

    # Render the calendar template with the calendar data, navigation parameters, month name/year, and events
    '''return render(request, 'student_module/student.html', {
        'calendar': calendar_data,
        'prev_date': prev_date,
        'next_date': next_date,
        'month_name': month_name,
        'year': year,
        'events': events,
        'student_details': student_details,
        'course_enrolled_list':courses,
        'stud_id':user_id,
        'course_count':enrolled_courses,
        'scheduled_course':course_details,
        
               }
    )'''
    #return render(request, 'student_module/student.html', context)

    # Get the current date from the URL parameters
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    date = datetime.strptime(date_str, '%Y-%m-%d')

    # Calculate the previous and next month values
    prev_month = date - relativedelta(months=1)
    next_month = date + relativedelta(months=1)

    prev_date = prev_month.replace(day=1).strftime('%Y-%m-%d')
    next_date = next_month.replace(day=1).strftime('%Y-%m-%d')

    # Generate the calendar data for the specified month
    cal = calendar.monthcalendar(date.year, date.month)

    # Get the current month's name and year
    month_name = date.strftime('%B')
    year = date.year

    # Prepare the calendar data with event information
    events = {
        5: ['Meeting 1', 'Meeting 2'],
        12: ['Appointment'],
        20: ['Conference'],
        25: ['Workshop', 'Training'],
    }

    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append((" ", []))
            else:
                events_for_day = events.get(day, [])
                week_data.append((day, events_for_day))
        calendar_data.append(week_data)

    # Render the calendar template with the calendar data, navigation parameters, month name/year, and events
    return render(request, 'student_module/student.html', {
        'calendar': calendar_data,
        'prev_date': prev_date,
        'next_date': next_date,
        'month_name': month_name,
        'year': year,
        'events': events,
        'student_details': student_details,
        'course_enrolled_list':courses,
        'stud_id':user_id,
        'course_count':enrolled_courses,
        'scheduled_course':course_details,
    })

@user_passes_test(is_student) 
def student_view_assignment_details(request, id, pk):
    if is_correct_student_cbatch_id(request.user.students_auth, id):
        return redirect("student-no-access")
    user = request.user
    batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk)
    comment_items = Activity_Comments.objects.filter(course_activity=activity).order_by('timestamp')
    file_relative_url = activity.activity_attachment.url 

    file_url = request.build_absolute_uri(file_relative_url)
    submission_grade = False
    submission_on_time = False
    if Activity_Submission.objects.filter(course_activity=activity,student_id=user.students_auth).values('activity_file').exists():
        submission_instance = Activity_Submission.objects.filter(course_activity=activity,student_id=user.students_auth).last()
        current_submission = submission_instance.activity_file
        initial_data = {'activity_file': current_submission}
        current_submission_filename = str(current_submission).split('/')[-1]
        # submission_upload_form = ActivitySubmissionUploadForm(initial=initial_data)
        #activity_file=current_submission
        submission_upload_form = ActivitySubmissionUploadForm()
        submission_grade = submission_instance.grade
        submission_on_time = True if submission_instance.date_submitted < activity.deadline else False
        # print(submission_instance.date_submitted)
        # print(activity.deadline)
    else:
        current_submission_filename = False
        submission_upload_form = ActivitySubmissionUploadForm()
    context = {
        'batch':batch,
        'act':activity,
        'cmt':comment_items,
        'file_url':file_url,
        'user':user,
        'submission_upload_form':submission_upload_form,
        'current_submission_filename':current_submission_filename,
        'submission_grade':submission_grade,
        'submission_on_time': submission_on_time,
             }
    if request.method == "POST":
        msg = request.POST['msg_area']
        user = request.user
        comment = Activity_Comments(course_activity = activity, uid = user,content = msg, timestamp=timezone.now())
        comment.save()
        return redirect('student_view_assignment_details',id=id,pk=pk)
    
    return render(request, 'student_module/assignment_details.html',context)

@user_passes_test(is_student) 
def upload_activity_submission(request, id, pk):
    if is_correct_student_cbatch_id(request.user.students_auth, id):
        return redirect("student-no-access")
    # Will try one file upload muna    
    student = request.user.students_auth
    # course_batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk)
    if request.method == 'POST':
        form = ActivitySubmissionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            prev_instances=Activity_Submission.objects.filter(course_activity=activity,student_id=student)
            if prev_instances:
                for prev_i in prev_instances:
                    file_path = prev_i.activity_file.path
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                prev_instances.delete()
            attachment=request.FILES['activity_file']
            instance = Activity_Submission(course_activity=activity,student_id=student,activity_file=attachment, date_submitted=timezone.now())
            instance.save()
            return redirect('student_view_assignment_details',id=id,pk=pk)
    return redirect('student_view_assignment_details',id=id,pk=pk)

@user_passes_test(is_student) 
def download_activity_attachment(request, id, pk):
    if is_correct_student_cbatch_id(request.user.students_auth, id):
        return redirect("student-no-access")
    # batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk) # Retrieve the object with the uploaded file

    # Perform any necessary checks or validations here

    # Retrieve the file path or file object from the model and open it
    file_path = activity.activity_attachment.path
    # print(file_path)
    file = open(file_path, 'rb')

    # Set the appropriate response headers
    filename=str(activity.activity_attachment.name).split('/')[-1]
    response = HttpResponse(file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

@user_passes_test(is_student) 
def download_activity_submission(request, id, pk):
    if is_correct_student_cbatch_id(request.user.students_auth, id):
        return redirect("student-no-access")
    student = request.user.students_auth
    course_batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk)
    submission = Activity_Submission.objects.filter(course_activity=activity,student_id=student).last()
    print(submission)
    file_path = submission.activity_file.path
    print(file_path)
    file = open(file_path, 'rb')

    # Set the appropriate response headers
    filename=str(submission.activity_file.name).split('/')[-1]
    response = HttpResponse(file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

@user_passes_test(is_student)   
def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')

@user_passes_test(is_student)   
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

def edit_student_comment(request, id , pk, fk):
    batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk) 
    comment_id = Activity_Comments.objects.get(id=fk)
    context = {
       'batch':batch,
        'act':activity,
        'comment':comment_id,
    }
    if request.method == 'POST':
         person = request.POST['target']
         user  = request.user
         msg = request.POST['txtmsg']
         comment_id.uid = user
         comment_id.content = msg
         comment_id.timestamp = timezone.now()
         comment_id.save(update_fields=['uid','content','timestamp'])
         return redirect('student_view_assignment_details', id=id,pk=pk)
    return render(request, "student_module/edit_comments.html", context)

def delete_student_comment(request, id, pk, fk):
    batch = Course_Enrollment.objects.get(pk=id)
    act= Course_Activity.objects.get(id=pk)
    comment_id = Activity_Comments.objects.get(id=fk)
    context = {
       'batch':batch,
        'act':act,
        'comment':comment_id,
        'id':id,
    }
    if request.method == 'POST':
        comment_id.delete()
        return redirect('student_view_assignment_details',id=id,pk=pk)
    return render(request, 'student_module/delete_comments.html',context)

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
         
         
        default_profile_pic = os.path.join(settings.STATIC_URL, 'student/assets/imgs/profile.png')
        profile_pic = False 
        
        if 'profile_pic' in request.FILES:
            profile_picture = request.FILES['profile_pic']
            profile_pic = f"{first_name}_{last_name}_{user_id}{os.path.splitext(profile_picture.name)[1]}"
            print(profile_pic)

        if profile_pic:
            media_root = settings.MEDIA_ROOT
            student_pic_folder = os.path.join(media_root, 'student_pic')
            os.makedirs(student_pic_folder, exist_ok=True)
            print("hereeee")
            
            file_path = os.path.join(student_pic_folder, profile_pic)
            print(file_path, "THFDS")
            with open(file_path, 'wb') as destination:
                for chunks in profile_picture.chunks():
                    destination.write(chunks) 
          

        student_auth_details.user.first_name = first_name
        student_auth_details.middlename = middlename
        student_auth_details.user.last_name = last_name
        student_auth_details.birthdate = birthdate

        if user_id in Student_Profile.objects.values_list('user_id', flat=True):
            #student_profile = Student_Profile.objects.get(user_id=user_id)
            print("I entered in line 152")
            student_profile.bio = bio
            student_profile.address = address
            student_profile.user_contact_no = user_contact_no
            student_profile.emergency_contact = emergency_contact
            student_profile.emergency_contact_no = emergency_contact_no

            #enters here if may record sa student_profile, used only for updating profile pic
            if profile_pic:
                student_profile.profile_pic = os.path.join('student_pic', profile_pic)

            

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
                profile_pic=os.path.join('student_pic', profile_pic))
            else:
                student_profile = Student_Profile(
                bio = bio,
                address = address,
                user_contact_no = user_contact_no,
                emergency_contact = emergency_contact,
                emergency_contact_no = emergency_contact_no,
                user_id=user_id,
                profile_pic="student_pic/profile.png")


        
        
        
        student_profile.save()
        student_auth_details.user.save()
        student_auth_details.save()
        

        
        return redirect('/sit-student/student_profile')
    
    return render(request, 'student_module/edit_profile.html', context)