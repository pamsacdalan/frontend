from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from apps.sitlms_app.models import *
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Instructor_Auth, Student_Enrollment, Students_Auth, Program
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from apps.sitlms_instructor.forms import ActivityForms
from apps.sitlms_instructor.models import Activity_Comments, ActivityPrivateComments, Course_Activity, Course_Announcement
from dateutil.parser import parse
from datetime import date, datetime
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_app.crud.enrolled_course import string_to_date, frequency_rev
import csv
from django.db.models import Q
from django.conf import settings
import os
from django.utils import timezone
import shutil

import json
from django.utils import timezone
from datetime import datetime, timedelta, date as date2
from django.contrib.auth.models import User
from apps.sitlms_instructor.models import Course_Announcement
from operator import itemgetter
from calendar import monthcalendar
import calendar
from django.template.loader import render_to_string
from dateutil.relativedelta import relativedelta

from apps.sitlms_student.models import Activity_Submission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def is_instructor(user):
    try:
        if hasattr(user,'instructor_auth'):
            return True
        raise PermissionDenied
    except Exception as e:
        raise PermissionDenied

def is_correct_instructor_cbatch_id(instructor, cbatch_id):
    try:
        if Course_Enrollment.objects.filter(course_batch=cbatch_id).first().instructor_id==instructor:
            pass
        else:
            return True
    except Exception as e:
        return True
    
def custom_403_1(request):
    # Pag pinasa ko with status=403, ayaw magload ng page :(
    # Dapat ganito: render(request, 'custom_403_1.html', status=403)
    return render(request, 'custom_403_1.html')

# Create your views here.
@user_passes_test(is_instructor)
def instructor(request):

    """ This function renders the instructor page """
    form = ActivityForms(request.POST)
    acts = Course_Activity.objects.all()
    
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    instructor_id = Instructor_Auth.objects.get(user_id=user_id)
    count_courses= Course_Enrollment.objects.filter(instructor_id=instructor_id).count()
    ongoing_course = Course_Enrollment.objects.filter(instructor_id=instructor_id,start_date__lte=datetime.today(),end_date__gte=datetime.today()).values().distinct()
    ongoing_count = len(ongoing_course)
    completed_course = Course_Enrollment.objects.filter(instructor_id=instructor_id,end_date__lte=datetime.today()).values('course_batch').distinct()
    completed_count = len(completed_course)

    
    context={
        'acts':acts,
        'form':form,
        'count_courses': count_courses,
        'ongoing_count': ongoing_count,
        'completed_count': completed_count
    }
    
    return render(request, 'instructor_module/instructor.html',context)

@user_passes_test(is_instructor)
def post_activity(request):
    if request.method == "POST":
        form = ActivityForms(request.POST)
        
        batch = Course_Enrollment.objects.filter(pk='test102').first()
        title = request.POST['activity_title']
        desc=request.POST['activity_desc']
        attachment = request.POST['activity_attachment']
        d1 = request.POST.get('deadline_0')
        d2 = request.POST.get('deadline_1')
        deadline = d1+" "+d2
        # due_date = request.POST['deadline']
        activity_post = Course_Activity(course_batch = batch,activity_title = title,activity_desc = desc,activity_attachment = attachment,deadline = deadline)
        # print(request.POST['activity_title'])
        # print(d1)
        # print(d2)
        activity_post.save()
        messages.success(request,"Success!")
        return redirect("/sit-instructor/instructor")
    else:
        form = ActivityForms()
    return render(request, 'instructor_module/instructor.html',{'form':form,})

@user_passes_test(is_instructor)
def instructor_view_enrolled_course(request):
    
    # admins = User.objects.filter(is_superuser=True)
    # for a in admins:
    #     print(a.id)


    template = loader.get_template('instructor_module/instructor_view_enrolled_course.html')

    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id


    instructor_id = Instructor_Auth.objects.get(user_id=user_id)
    course_enrolled = Course_Enrollment.objects.filter(instructor_id=instructor_id).values()

    for index in range(len(course_enrolled)):
        course_num = course_enrolled[index]['course_id_id']
        for value in Course_Catalog.objects.values('course_id', 'course_title'):
            
            if course_num == value['course_id']:
                course_enrolled[index]['course_id_id'] = value['course_title']
                # print(value['course_title'])
    
    # print(course_enrolled)

    context = {'course_enrolled_list':course_enrolled,
                }
    

    return HttpResponse(template.render(context,request))


@user_passes_test(is_instructor)
def view_students(request, id):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    template = loader.get_template('instructor_module/instructor_view_student.html')

    # course = Course_Enrollment.objects.get(course_batch=id)
    students = Student_Enrollment.objects.filter(course_batch=id).values('student_id_id')
    # student_list = students.values().order_by('student_id_id')
    # student_ids = student_list.values_list('student_id')
    student_auth_details = Students_Auth.objects.filter(id__in=students).values('user_id', 'middlename', 'program_id_id').order_by('user_id')
    user_ids = student_auth_details.values_list('user_id')
    student_details = User.objects.filter(id__in=user_ids).values('first_name', 'last_name', 'username').order_by('id')
    
    # print(student_details)
    # student_details = sorted(student_details, key=lambda student_details: student_details.last_name)

    program_ids = student_auth_details.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values('program_id','program_code','program_title')  # program code to be added to new_list
    
    
    course_id = Course_Enrollment.objects.filter(course_batch=id).values('course_id_id')[0]['course_id_id']
    course = Course_Catalog.objects.filter(course_id=course_id).values()[0]
    

    count = len(students)
    
    # create a new list to pass as context
    new_list = []


    # for x in range(count):
    #     for program in program_code:
    #         if student_auth_details[x]['program_id_id'] == program['program_id']:
    #             new_list.append({**student_auth_details[x], **student_details[x], **program})

    for x in range(count):
        for program in program_code:
            if student_auth_details[x]['program_id_id'] == program['program_id']:
                if student_auth_details[x]['user_id'] in Student_Profile.objects.values_list('user_id', flat=True):
                    profile_path = Student_Profile.objects.filter(user_id=student_auth_details[x]['user_id']).values('profile_pic')
                    profile_path = profile_path[0]['profile_pic']
                    profile_path = os.path.normpath(profile_path)
                    if profile_path.startswith(settings.MEDIA_URL):
                        profile_path = profile_path.replace(settings.MEDIA_URL, settings.STATIC_URL, 1)
                    profile_path = profile_path.replace('\\', '/')
                    print(profile_path)
                    
                    new_list.append({**student_auth_details[x], **student_details[x], **program, 'profile_pic': profile_path})
                else:
                    new_list.append({**student_auth_details[x], **student_details[x], **program, 'profile_pic': ''})

    def sort_by_name(dictionary):
        return dictionary['last_name'].lower()

    new_list = sorted(new_list, key=sort_by_name)
    # print(new_list)

    # for pagination
    page = request.GET.get('page', 1) # default page (default to first page)
        
    items_per_page = 10
    paginator = Paginator(new_list, items_per_page)
    
    try:
            student_list = paginator.page(page)
    except PageNotAnInteger:
            student_list = paginator.page(1)
    except EmptyPage:
            student_list = paginator.page(paginator.num_pages)

    context = {'new_list': new_list,
               'id':id,
               'count': count,
               'course': course,
               'student_list': student_list,
                }
    
    return HttpResponse(template.render(context,request))  

@user_passes_test(is_instructor)
def change_schedule(request, id): #need notif na nasend na yung request.. helllppp
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    # template = loader.get_template('instructor_module/instructor_change_schedule.html')
    enrolled_course = Course_Enrollment.objects.get(course_batch=id) #ex: Python101
    course_batch = enrolled_course.course_batch
    old_sd = enrolled_course.start_date
    old_ed = enrolled_course.end_date
    old_st = enrolled_course.start_time
    old_et = enrolled_course.end_time
    old_frequency = frequency_rev(enrolled_course.frequency)
    list_frequency = ["Once","Daily","Weekly"]

    # print(old_st, type(old_st))
    # print(enrolled_course)
    # print(type(old_sd), type(old_ed), type(old_st), type(old_et))

    context = {
        'old_sd' : old_sd,
        'old_ed' : old_ed,
        'old_st' : old_st,
        'old_et' : old_et,
        'enrolled_course' : enrolled_course,
        'old_frequency': old_frequency,
        'lof': list_frequency
    }

    if request.method == "POST":

        start_date  = request.POST['start_date']
        end_date  = request.POST['end_date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']     
        new_frequency = request.POST['new_frequency']

        # print(type(start_date), type(end_date), type(start_time), type(end_time))

        if new_frequency == "Once":
            new_frequency=0
        elif new_frequency == "Daily":
            new_frequency=1
        else:
            new_frequency=7

        change_schedule = Change_Schedule(
            course_batch = Course_Enrollment.objects.get(course_batch=course_batch), 
            old_start_date = old_sd,
            old_end_date = old_ed,
            old_start_time = old_st,
            old_end_time = old_et,
            old_frequency = enrolled_course.frequency,
            new_start_date  = start_date,
            new_end_date  = end_date,
            new_start_time = start_time,
            new_end_time = end_time,
            new_frequency = new_frequency
        )   
        change_schedule.save()

        notif_type = "Change Schedule"

        Notify(request, id, notif_type)

        return redirect('view_courses')   
    
    return render(request, "instructor_module/instructor_change_schedule.html", context)

@user_passes_test(is_instructor)
def view_pending_requests(request):
    template = loader.get_template('instructor_module/instructor_view_pending_requests.html')
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    instructor_id = Instructor_Auth.objects.get(user_id=user_id)
    course_enrolled = Course_Enrollment.objects.filter(instructor_id=instructor_id).values('course_batch') 
    # print(course_enrolled)

    pending_requests = Change_Schedule.objects.filter(status='Pending', course_batch__in=course_enrolled).values()
    approved_rejected_requests = Change_Schedule.objects.filter(Q(status='Approved')| Q(status='Rejected'), course_batch__in=course_enrolled).values()
    
    context = {'pending_requests':pending_requests,
                'approved_rejected_requests': approved_rejected_requests}

    return HttpResponse(template.render(context,request))

@user_passes_test(is_instructor)
def view_assignments (request,id):
    """ This function renders the instructor assignment page """
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    acts = Course_Activity.objects.filter(course_batch=id)
    course_id = Course_Enrollment.objects.filter(course_batch=id).values('course_id_id')[0]['course_id_id']
    course = Course_Catalog.objects.filter(course_id=course_id).values()[0]
    count_acts = Course_Activity.objects.filter(course_batch=id).values().count()
    
    context={
        'acts':acts,
        'id':id,
        'course': course,
        'count_acts': count_acts
    }
    # print(acts)
    return render(request, 'instructor_module/view_assignments.html',context)

@user_passes_test(is_instructor)
def add_assignment(request, id):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    if request.method == "POST":
        form = ActivityForms(request.POST, request.FILES)
        
        batch = Course_Enrollment.objects.filter(pk=id).first()
        title = request.POST['activity_title']
        desc=request.POST['activity_desc']
        attachment=request.FILES.get('activity_attachment')
        d1 = request.POST.get('deadline_0')
        d2 = request.POST.get('deadline_1')
        deadline = d1+" "+d2
        date_object = timezone.make_aware(datetime.strptime(deadline, '%Y-%m-%d %H:%M'))
        score = request.POST['scores']
        percent = request.POST['percentage']

        if date_object <= timezone.now():
            # return render(request, 'instructor_module/add_assignment.html',{'form':form, 'id': id, 'error_msg': 'Deadline should be in the future'})
            messages.error(request,'Deadline should be in the future. Please re-create assignment.')
            return redirect("view_assignments",  id=id)
        elif attachment is not None and attachment.size > 25 * 1024 * 1024:
            messages.error(request,'Maximum file size is 25MB. Please re-create assignment.')
        else:
            activity_post = Course_Activity(course_batch = batch,activity_title = title,activity_desc = desc,activity_attachment = attachment,deadline = date_object, max_score = score, grading_percentage = percent)
            activity_post.save()
            messages.success(request,"Success!")
            return redirect("view_assignments",  id=id)
    else:
        form = ActivityForms()
    return redirect("view_assignments",  id=id)
    # return render(request, 'instructor_module/add_assignment.html',{'form':form, 'id': id,})

@user_passes_test(is_instructor)
def update_assignment(request,id,pk):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    batch = Course_Enrollment.objects.get(pk=id)
    act= Course_Activity.objects.get(id=pk)
    context = {
        'batch':batch,
        'act':act,
    }
    if request.method == "POST":
        title = request.POST['title']
        desc = request.POST['description']
        # attach = request.FILES['attachment']
        end_date = request.POST['d1']
        end_time = request.POST['t1']
        dt = end_date+" "+end_time
        items = request.POST['items']
        grade = request.POST['gr']
        

        act.activity_title = title
        act.activity_desc = desc
        # act.activity_attachment = attach
        act.deadline = dt
        act.grading_percentage = grade
        act.max_score = items
        act.save(update_fields=['activity_title','activity_desc','deadline','grading_percentage','max_score'])
        return HttpResponseRedirect(reverse('view_assignments', kwargs={'id': id}))
    return render(request, "instructor_module/edit_assignment.html", context)

@user_passes_test(is_instructor)
def delete_assignment(request, id, pk):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    batch = Course_Enrollment.objects.get(pk=id)
    act= Course_Activity.objects.get(id=pk)
    context = {
        'batch':batch,
        'act':act,
        'id':id,
    }
    if request.method == 'POST':
        prev_instances=act.activity_attachment if act.activity_attachment else False
        # print(prev_instances)
        if prev_instances:
            file_path = prev_instances.path
            # print(file_path)
            if os.path.isfile(file_path):
                # print(3)
                os.remove(file_path)
                folder_path = os.path.dirname(file_path)
                # print(folder_path)
                shutil.rmtree(folder_path)
            prev_instances.delete()
        act.delete()
        return redirect('view_assignments',id=id)
    return render(request,'instructor_module/delete_assignment.html',context)

@user_passes_test(is_instructor)
def instructor_course(request, id):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    template = loader.get_template('instructor_module/instructor_course.html')

    course_id = Course_Enrollment.objects.filter(course_batch=id).values('course_id_id')[0]['course_id_id']
    course = Course_Catalog.objects.filter(course_id=course_id).values()[0]
    
    announcement_details = Course_Announcement.objects.filter(course_batch=id).order_by('-date_posted').values()

    user = request.user
    user_id = user.id
    firstname = User.objects.values_list('first_name', flat=True).get(id=user_id)
    lastname = User.objects.values_list('last_name', flat=True).get(id=user_id)
        
    author_name = firstname + " " + lastname
    
    if user_id in Student_Profile.objects.values_list('user_id', flat=True):
        instructor_profile = Student_Profile.objects.get(user_id=user_id)

        profile_pic = instructor_profile.profile_pic
    else:
        profile_pic = ""
    

    context = {
        'course_batch': id,
        'course': course,
        'announcements':announcement_details,
        'author': author_name,
        'profile_pic': profile_pic,
    }

    return HttpResponse(template.render(context,request))  

@user_passes_test(is_instructor)
def create_announcement(request,id):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    template = loader.get_template('instructor_module/instructor_course.html')
    
    if request.method == "POST":
        text = request.POST['announcement_text']

        user = request.user
        user_id = user.id

        instructor_id = Instructor_Auth.objects.filter(user_id=user_id).values_list('id',flat=True)[0]

        announcement = Course_Announcement(
            announcement_text=text,
            course_batch=Course_Enrollment.objects.get(course_batch=id),
            author_id=instructor_id
        )

        announcement.save()

        return redirect(f'/sit-instructor/instructor/course/{id}')
    
    context = {'course_batch':id}

    return HttpResponse(template.render(context,request))  

@user_passes_test(is_instructor)
def remove_announcement(request, course_batch, schedule_id):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, course_batch):
        return redirect("instructor-no-access")
    announcement = Course_Announcement.objects.get(id=schedule_id)

    if request.method == "POST":
        announcement.delete()
        return HttpResponseRedirect(reverse('view_instructor_course', kwargs={'id': course_batch}))
    
    return render(request, "instructor_module/instructor_course.html", {'course_batch': course_batch})

@user_passes_test(is_instructor)
def edit_announcement(request, course_batch, schedule_id):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, course_batch):
        return redirect("instructor-no-access")
    announcement = Course_Announcement.objects.get(id=schedule_id)
    context =  {'course_batch': course_batch, 'announcement': announcement}

    if request.method == "POST":
        announcement_text = request.POST['announcement_text']
        announcement.announcement_text = announcement_text
        announcement.date_posted = datetime.now()

        announcement.save(update_fields=['announcement_text', 'date_posted'])

        return HttpResponseRedirect(reverse('view_instructor_course', kwargs={'id': course_batch}))
    
    return render(request, "instructor_module/edit_announcement.html", context)
    # return render(request, "instructor_module/instructor_course.html", context)

@user_passes_test(is_instructor)
def activity_comments(request, id, pk):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk)
    comment_items = Activity_Comments.objects.filter(course_activity=activity).order_by('timestamp')
    count = comment_items.values().count() #ADDED for display of no. of comments
    file_relative_url = activity.activity_attachment.url if activity.activity_attachment else "#" # Get the relative URL of the uploaded file
    course_id = Course_Enrollment.objects.filter(course_batch=batch).values('course_id_id')[0]['course_id_id']
    course = Course_Catalog.objects.filter(course_id=course_id).values()[0]
    
    # Construct the absolute URL by prepending the protocol and domain
    file_url = request.build_absolute_uri(file_relative_url)

    comment_items_w_pic = []
    for x in comment_items:
        if x.uid.pk in Student_Profile.objects.values_list('user_id', flat=True):
            profile_path = Student_Profile.objects.get(user_id=x.uid).profile_pic
            comment_items_w_pic.append({'items':x,'profile_pic':profile_path})
        else:
            comment_items_w_pic.append({'items':x,'profile_pic':False})

    context = {
        'batch':batch,
        'act':activity,
        #'cmt':comment_items,
        'cmt':comment_items_w_pic,
        'file_url':file_url,
        'count': count,
        'course': course
             }
    if request.method == "POST":
        msg = request.POST['msg_area']
        user = request.user
        comment = Activity_Comments(course_activity = activity, uid = user,content = msg, timestamp=timezone.now())
        comment.save()
        return redirect('activity_comments',id=id,pk=pk)
    return render(request, 'instructor_module/activity_comment.html',context)

@user_passes_test(is_instructor)
def download_activity_attachment(request, id, pk):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
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

@user_passes_test(is_instructor)
def cancel_request(request, id):
    schedule = Change_Schedule.objects.filter(id=id)
    schedule.update(status='Cancelled', approval_date = datetime.now() )

    return redirect('/sit-instructor/instructor/view_courses/view_pending_requests/')

@user_passes_test(is_instructor)
def export_csv(request, id):
    students = Student_Enrollment.objects.filter(course_batch=id).values('student_id_id')
    student_auth_details = Students_Auth.objects.filter(id__in=students).values('user_id', 'middlename', 'program_id_id').order_by('user_id')
    user_ids = student_auth_details.values_list('user_id')
    student_details = User.objects.filter(id__in=user_ids).values('first_name', 'last_name', 'username', 'id').order_by('id')
    student_details = sorted(list(student_details), key=lambda x: x['last_name'].lower())
    
    program_ids = student_auth_details.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values('program_id','program_code')

    response = HttpResponse(content_type='text/csv')
    
    filename = id + '_students.csv'
    
    response['Content-Disposition'] = f'attachment; filename={filename}'
    writer = csv.writer(response)
    writer.writerow(['Program', 'Last_Name', 'First_Name', 'Email'])
    
    
    for student in student_details:
        program = Students_Auth.objects.values('program_id').get(user_id = student['id'])
        program_code = Program.objects.values('program_code').get(program_id = program['program_id'])
        #additional = program.program_id
        writer.writerow([program_code['program_code'], student['last_name'], student['first_name'], student['username']])
        
    return response


    
@user_passes_test(is_instructor)
def edit_comments(request,id,pk,fk):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
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
         comment_id.save(update_fields=['uid','content'])
         return redirect('activity_comments', id=id,pk=pk)
    return render(request, "instructor_module/edit_comments.html", context)

@user_passes_test(is_instructor)
def delete_comments(request,id,pk,fk):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
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
        return redirect('activity_comments',id=id,pk=pk)
    return render(request, 'instructor_module/activity_comment.html',context)

@user_passes_test(is_instructor)
def download_student_activity_submission(request, id, pk, student):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    student = Students_Auth.objects.get(pk=student)
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

@user_passes_test(is_instructor)
def student_work(request, id, pk):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk)
    list_of_submissions = Activity_Submission.objects.filter(course_activity=activity).values('student_id','date_submitted', 'activity_file', 'grade','id')
    dict_of_submissions = {}
    list_of_submissions_2 = []
    for x in list_of_submissions:
        student = Students_Auth.objects.get(pk=x['student_id'])
        filename=str(x['activity_file']).split('/')[-1]
        # is_submission_on_time = True if x['date_submitted'] < activity.deadline else False
        # print(is_submission_on_time)
        #last_private_comment = False
        last_private_comment = ActivityPrivateComments.objects.filter(course_activity=activity,student=student).order_by("timestamp").last().content if ActivityPrivateComments.objects.filter(course_activity=activity,student=student).exists() else False
        # print(last_private_comment)
        list_of_submissions_2.append([student.user.last_name, student.user.first_name, filename, x['date_submitted'], student.pk, x['id'], x['grade'], last_private_comment])
    # items_no = int(activity.max_score)
    # percent = activity.grading_percentage
    students_submitted = Activity_Submission.objects.filter(course_activity=activity).values('student_id')
    students_not_submitted = Student_Enrollment.objects.filter(course_batch=batch).exclude(student_id__in=students_submitted).values('student_id')
    students_nonsubmit_context = []
    # print(students_not_submitted)
    for x in students_not_submitted:
        student = Students_Auth.objects.get(pk=x['student_id'])
        last_private_comment = ActivityPrivateComments.objects.filter(course_activity=activity,student=student).order_by("timestamp").last().content if ActivityPrivateComments.objects.filter(course_activity=activity,student=student).exists() else False
        students_nonsubmit_context.append([student.user.last_name, student.user.first_name, student.pk, last_private_comment])
    context = {
        'list_of_submissions': list_of_submissions_2,
        'batch':batch,
        'act':activity,
        'list_of_students_nonsubmit':students_nonsubmit_context,
    }
    # print(list_of_submissions)
    return render(request, 'instructor_module/student_submissions.html',context)

def save_activity_grades(request,id,pk,fk):
    batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk)
    student = Activity_Submission.objects.get(pk=fk)

    if request.method =="POST":
        grade = request.POST['score']
        if grade == "":
            grade = None
        student.grade = grade
        student.save(update_fields=['grade'])
       
        return redirect('student_work', id=id,pk=pk)
    return render(request, "instructor_module/edit_comments.html")



def edit_profile(request):
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    instructor_auth_details = Instructor_Auth.objects.get(user_id=user_id)

    if user_id in Student_Profile.objects.values_list('user_id', flat=True):
        instructor_profile = Student_Profile.objects.get(user_id=user_id)
        instructor_profile.profile_pic = str(instructor_profile.profile_pic).replace("\\","/")
        instructor_profile.save()

        instructor_details ={'first_name':instructor_auth_details.user.first_name, 
                            'middlename':instructor_auth_details.middlename,
                            'last_name':instructor_auth_details.user.last_name,
                            'birthdate':instructor_auth_details.birthdate,
                            'bio':instructor_profile.bio,
                            'address':instructor_profile.address,
                            'user_contact_no':instructor_profile.user_contact_no,
                            'emergency_contact':instructor_profile.emergency_contact,
                            'emergency_contact_no':instructor_profile.emergency_contact_no,
                            'profile_pic':instructor_profile.profile_pic,
                            'email': instructor_auth_details.user.username,
                            'emp_no': instructor_auth_details.user_id
                        }
    else:
        instructor_details ={ 'first_name':instructor_auth_details.user.first_name, 
                        'middlename':instructor_auth_details.middlename,
                        'last_name':instructor_auth_details.user.last_name,
                        'birthdate':instructor_auth_details.birthdate,
                        'bio':"",
                        'address':"",
                        'user_contact_no':"",
                        'emergency_contact':"",
                        'emergency_contact_no':"",
                        'profile_pic':"",
                        'email': instructor_auth_details.user.username,
                        'emp_no': instructor_auth_details.user_id
                    }   
        
    context = {'instructor_details': instructor_details      
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
            profile_picture = request.FILES['profile_pic']
            profile_pic = f"{user_id}{os.path.splitext(profile_picture.name)[1]}"


        if profile_pic:
            static_dirs = settings.STATICFILES_DIRS  # Get the STATICFILES_DIRS list from Django settings
            instructor_pic_folder = os.path.join(static_dirs[0], 'instructor_pic')
            os.makedirs(instructor_pic_folder, exist_ok=True)

            file_path = os.path.join(instructor_pic_folder, profile_pic)
            
            with open(file_path, 'wb') as destination:
                for chunks in profile_picture.chunks():
                    destination.write(chunks)




        instructor_auth_details.user.first_name = first_name
        instructor_auth_details.middlename = middlename
        instructor_auth_details.user.last_name = last_name
        instructor_auth_details.birthdate = birthdate

        if user_id in Student_Profile.objects.values_list('user_id', flat=True):
            # student_profile = Student_Profile.objects.get(user_id=user_id)
            print("I entered in line 152")
            instructor_profile.bio = bio
            instructor_profile.address = address
            instructor_profile.user_contact_no = user_contact_no
            instructor_profile.emergency_contact = emergency_contact
            instructor_profile.emergency_contact_no = emergency_contact_no

            # enters here if there is a record in student_profile, used only for updating profile pic
            if profile_pic:
                instructor_profile.profile_pic = str(os.path.join(settings.STATIC_URL, 'instructor_pic', profile_pic)).replace("\\","/")

        else:
            # enters here if there is no record yet in student_profile

            if profile_pic:
                instructor_profile = Student_Profile(
                    bio=bio,
                    address=address,
                    user_contact_no=user_contact_no,
                    emergency_contact=emergency_contact,
                    emergency_contact_no=emergency_contact_no,
                    user_id=user_id,
                    profile_pic=str(os.path.join(settings.STATIC_URL, 'instructor_pic', profile_pic)).replace("\\","/")
                )
            else:
                instructor_profile = Student_Profile(
                    bio=bio,
                    address=address,
                    user_contact_no=user_contact_no,
                    emergency_contact=emergency_contact,
                    emergency_contact_no=emergency_contact_no,
                    user_id=user_id,
                    profile_pic=os.path.join(settings.STATIC_URL, 'student/assets/imgs/profile.png')
                )

        
        instructor_profile.save()
        instructor_auth_details.user.save()
        instructor_auth_details.save()

        return redirect('/sit-instructor/instructor')


    return render(request, 'instructor_module/edit_profile.html', context)

def view_report_issues(request):
    return render(request, 'instructor_module/report_issue.html')

def report_issues(request):
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    if request.method == "POST":
        student_report_issues = Instructor_Auth.objects.get(user_id=user_id)
        firstname = User.objects.get(id=user_id).first_name
        lastname = User.objects.get(id=user_id).last_name
        student_access = student_report_issues.access_type
        subject = request.POST['subject']
        msg = request.POST['message']

        issue = SubmitIssue(sender_firstname = firstname,sender_lastname = lastname,sender_access_type= student_access,sender_subject = subject,sender_message = msg)
        issue.save()
        #DEBUG
        # print(f'{firstname} | {lastname} | {student_access}')
        # print(f'{subject} \n {msg}')
    return redirect('/sit-instructor/instructor')


@user_passes_test(is_instructor)
def private_comments(request, id, pk, student):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    #batch = Course_Enrollment.objects.get(pk=id)
    #activity = Course_Activity.objects.get(id=pk)
    #student = Activity_Submission.objects.get(pk=student)
    comments = ActivityPrivateComments.objects.filter(course_activity=Course_Activity.objects.get(id=pk),student=student).order_by("timestamp")
    student_submission = str(Activity_Submission.objects.get(course_activity=pk, student_id=student).activity_file).split('/')[-1] if Activity_Submission.objects.filter(course_activity=pk, student_id=student).exists() else False
    marks = Activity_Submission.objects.get(course_activity=pk, student_id=student).grade if Activity_Submission.objects.filter(course_activity=pk, student_id=student).exists() and Activity_Submission.objects.get(course_activity=pk, student_id=student).grade else False
    max_score = Course_Activity.objects.get(id=pk).max_score
    context = {
        "comments":comments,
        'batch':Course_Enrollment.objects.get(pk=id),
        'act':Course_Activity.objects.get(id=pk),
        'student':Students_Auth.objects.get(pk=student),
        'student_submission':student_submission,
        'marks': marks,
        'max_score':max_score,
    }
    return render(request, 'instructor_module/act_private_comments.html', context)

@user_passes_test(is_instructor)
def add_private_comment_instructor(request, id, pk, student):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    if request.method=="POST":
        instance = ActivityPrivateComments(course_activity=Course_Activity.objects.get(id=pk),student=Students_Auth.objects.get(pk=student),uid=request.user,content=request.POST.get("comment_content"))
        instance.save()
    return redirect('instructor_private_comments', id=id,pk=pk,student=student)

@user_passes_test(is_instructor)
def delete_private_comment_instructor(request, id, pk, student, comment_id):
    if is_correct_instructor_cbatch_id(request.user.instructor_auth, id):
        return redirect("instructor-no-access")
    instance = ActivityPrivateComments.objects.get(pk=comment_id)
    instance.delete()
    return redirect('instructor_private_comments', id=id,pk=pk,student=student)




def calendar(request):
    """ function to render the schedule of the instructor on a calendar"""

    with open('./static/holidays.json', 'r') as openfile:
        sample_holiday_list = json.load(openfile)
    
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id

    instructor_auth_details = Instructor_Auth.objects.get(user_id=user_id)
    instructor_id = instructor_auth_details.id
    instructor_courses = Course_Enrollment.objects.filter(instructor_id_id=instructor_id).values()
    instructor_courses = [x for x in instructor_courses] # convert to list
    course_count = len(instructor_courses)

    sample_colors = [
        "#800000" , "#722F37", "#800020", "#C8385A", "#7B0000", "#B03060", "#800000", "#800000"
    ]

    event_list = []

    for i in sample_holiday_list:
        item = {}
        item['start'] = str(i)
        item['title'] = sample_holiday_list[i]['description']
        item['color'] = '#1C0118' # holiday background color
        event_list.append(item)

    for x in range(course_count):
        course_id = instructor_courses[x]['course_id_id']
        course_batch = instructor_courses[x]['course_batch']
        schedules = Schedule.objects.filter(course_batch=course_batch).values()

        start_time = instructor_courses[x]['start_time']
        end_time = instructor_courses[x]['end_time']

        for i in schedules:
            item = {}
            session_date_str = str(i['session_date'])
            item['start'] = datetime.combine(i['session_date'], start_time).isoformat()
            item['end'] = datetime.combine(i['session_date'], end_time).isoformat()
            if session_date_str in sample_holiday_list:
                continue
            item['title'] = instructor_courses[x]['course_batch']
            item['course_id'] = instructor_courses[x]['course_id_id']
            item['full_desc'] = Course_Catalog.objects.get(course_id = course_id).course_desc # add course desc to dictionary
            item['url'] = instructor_courses[x]['session_details'].lower()
            item['course_batch'] = course_batch

            try:
                item['color'] = sample_colors[x]
            except:
                item['color'] = '#A7000'

            event_list.append(item)

    return render(request, 'instructor_module/calendar.html', {
        'event_list':json.dumps(event_list),
    })


def Notify(request, id, notif_type):
    user = request.user
    queryset = get_user_model().objects.filter(id=user.id)
    user_id = queryset.first().id
    instructor_auth_details = Instructor_Auth.objects.get(user_id=user_id)
    instructor_id = Instructor_Auth.objects.filter(user_id=user_id).values('id')
    course_id = Course_Enrollment.objects.filter(course_batch=id).values_list('course_id_id', flat=True)
    course_title = Course_Catalog.objects.filter(course_id=course_id[0]).values('course_title')
    course_title = course_title[0]['course_title']

    
    if notif_type == "Change Schedule":
        admins = User.objects.filter(is_staff=True)
        for a in admins:
            notification = Notification(
                            recipient = User.objects.get(id=a.id),
                            message = f"Change Schedule Request for {course_title} from {instructor_auth_details.user.first_name}",
                            sender = user_id,
                            notif_type = notif_type,
            )
            notification.save()