from django.shortcuts import render
from django.urls import reverse
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Instructor_Auth, Student_Enrollment, Students_Auth, Program
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib import messages
from apps.sitlms_app.models import Course_Enrollment
from apps.sitlms_instructor.forms import ActivityForms
from apps.sitlms_instructor.models import Course_Activity, Course_Announcement
from dateutil.parser import parse
from datetime import date, datetime
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from functools import partial


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
            raise PermissionDenied
    except Exception as e:
        raise PermissionDenied

# Create your views here.
@user_passes_test(is_instructor)
def instructor(request):
    """ This function renders the student page """
    form = ActivityForms(request.POST)
    acts = Course_Activity.objects.all()
    context={
        'acts':acts,
        'form':form,
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
        print(request.POST['activity_title'])
        print(d1)
        print(d2)
        activity_post.save()
        messages.success(request,"Success!")
        return redirect("/sit-instructor/instructor")
    else:
        form = ActivityForms()
    return render(request, 'instructor_module/instructor.html',{'form':form,})

@user_passes_test(is_instructor)
def instructor_view_enrolled_course(request):
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
                print(value['course_title'])
    
    # print(course_enrolled)

    option_course_title = Course_Catalog.objects.all()
    context = {'course_enrolled_list':course_enrolled
                }
    

    return HttpResponse(template.render(context,request))


@user_passes_test(is_instructor)
def view_students(request, id):
    is_correct_instructor_cbatch_id(request.user.instructor_auth, id)
    template = loader.get_template('instructor_module/instructor_view_student.html')

    # course = Course_Enrollment.objects.get(course_batch=id)
    students = Student_Enrollment.objects.filter(course_batch=id).values('student_id_id')
    # student_list = students.values().order_by('student_id_id')
    # student_ids = student_list.values_list('student_id')
    student_auth_details = Students_Auth.objects.filter(id__in=students).values('user_id', 'middlename', 'program_id_id').order_by('user_id')
    user_ids = student_auth_details.values_list('user_id')
    student_details = User.objects.filter(id__in=user_ids).values('first_name', 'last_name', 'username').order_by('id')

    program_ids = student_auth_details.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values('program_id','program_code')  # program code to be added to new_list

    count = len(students)

    # create a new list to pass as context
    new_list = []


    for x in range(count):
        for program in program_code:
            if student_auth_details[x]['program_id_id'] == program['program_id']:
                new_list.append({**student_auth_details[x], **student_details[x], **program})


    context = {'new_list': new_list,
               'id':id
                }
    
    return HttpResponse(template.render(context,request))  


@user_passes_test(is_instructor)
def change_schedule(request, id):
    is_correct_instructor_cbatch_id(request.user.instructor_auth, id)
    template = loader.get_template('instructor_module/instructor_change_schedule.html')

    context = {
        'test': 'test'
    }
    return HttpResponse(template.render(context,request))  

@user_passes_test(is_instructor)
def view_assignments (request,id):
    """ This function renders the student page """
    is_correct_instructor_cbatch_id(request.user.instructor_auth, id)
    acts = Course_Activity.objects.filter(course_batch=id)
    context={
        'acts':acts,
        'id':id,
    }
    # print(acts)
    return render(request, 'instructor_module/view_assignments.html',context)

@user_passes_test(is_instructor)
def add_assignment(request, id):
    is_correct_instructor_cbatch_id(request.user.instructor_auth, id)
    if request.method == "POST":
        form = ActivityForms(request.POST, request.FILES)
        
        batch = Course_Enrollment.objects.filter(pk=id).first()
        title = request.POST['activity_title']
        desc=request.POST['activity_desc']
        attachment=request.FILES['activity_attachment']
        d1 = request.POST.get('deadline_0')
        d2 = request.POST.get('deadline_1')
        deadline = d1+" "+d2
        date_object = datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        score = request.POST['scores']
        percent = request.POST['percentage']

        if date_object <= datetime.now():
            return render(request, 'instructor_module/add_assignment.html',{'form':form, 'id': id, 'error_msg': 'Deadline should be in the future'})
        else:
            activity_post = Course_Activity(course_batch = batch,activity_title = title,activity_desc = desc,activity_attachment = attachment,deadline = deadline, max_score = score, grading_percentage = percent)
            activity_post.save()
            messages.success(request,"Success!")
            return redirect("view_assignments",  id=id)
    else:
        form = ActivityForms()
    return render(request, 'instructor_module/add_assignment.html',{'form':form, 'id': id,})

def update_assignment(request,id,pk):
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

def delete_assignment(request, id, pk):
    batch = Course_Enrollment.objects.get(pk=id)
    act= Course_Activity.objects.get(id=pk)
    context = {
        'batch':batch,
        'act':act,
        'id':id,
    }
    if request.method == 'POST':
        act.delete()
        return redirect('view_assignments',id=id)
    return render(request,'instructor_module/delete_assignment.html',context)

@user_passes_test(is_instructor)
def instructor_course(request, id):
    is_correct_instructor_cbatch_id(request.user.instructor_auth, id)
    template = loader.get_template('instructor_module/instructor_course.html')

    course_id = Course_Enrollment.objects.filter(course_batch=id).values('course_id_id')[0]['course_id_id']
    course = Course_Catalog.objects.filter(course_id=course_id).values()[0]
    
    announcement_details = Course_Announcement.objects.filter(course_batch=id).values()

    user = request.user
    user_id = user.id
    firstname = User.objects.values_list('first_name', flat=True).get(id=user_id)
    lastname = User.objects.values_list('last_name', flat=True).get(id=user_id)

    author_name = firstname + " " + lastname

    context = {
        'course_batch': id,
        'course': course,
        'announcements':announcement_details,
        'author': author_name,
    }

    return HttpResponse(template.render(context,request))  

@user_passes_test(is_instructor)
def create_announcement(request,id):
    is_correct_instructor_cbatch_id(request.user.instructor_auth, id)
    template = loader.get_template('instructor_module/create_announcement.html')
    
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
    is_correct_instructor_cbatch_id(request.user.instructor_auth, course_batch)
    announcement = Course_Announcement.objects.get(id=schedule_id)

    if request.method == "POST":
        announcement.delete()
        return HttpResponseRedirect(reverse('view_instructor_course', kwargs={'id': course_batch}))
    
    return render(request, "instructor_module/delete_announcement.html", {'course_batch': course_batch})

@user_passes_test(is_instructor)
def edit_announcement(request, course_batch, schedule_id):
    is_correct_instructor_cbatch_id(request.user.instructor_auth, course_batch)
    announcement = Course_Announcement.objects.get(id=schedule_id)
    context =  {'course_batch': course_batch, 'announcement': announcement}

    if request.method == "POST":
        announcement_text = request.POST['announcement_text']
        announcement.announcement_text = announcement_text
        announcement.date_posted = datetime.now()

        announcement.save(update_fields=['announcement_text', 'date_posted'])

        return HttpResponseRedirect(reverse('view_instructor_course', kwargs={'id': course_batch}))
    
    return render(request, "instructor_module/edit_announcement.html", context)

def render_calendar(request):
    return render(request,'instructor/calendar.html')