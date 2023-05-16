from django.shortcuts import render
from django.urls import reverse
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Instructor_Auth, Student_Enrollment, Students_Auth, Program
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from apps.sitlms_app.models import Course_Enrollment
from apps.sitlms_instructor.forms import ActivityForms
from apps.sitlms_instructor.models import Course_Activity
from dateutil.parser import parse
from datetime import date, datetime



# Create your views here.

def instructor(request):
    """ This function renders the student page """
    form = ActivityForms(request.POST)
    acts = Course_Activity.objects.all()
    context={
        'acts':acts,
        'form':form,
    }
    print(acts)
    return render(request, 'instructor_module/instructor.html',context)

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



def view_students(request, id):
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

    print(new_list)


    context = {'new_list': new_list,
               'id':id
                }
    
    return HttpResponse(template.render(context,request))  


def change_schedule(request, id):
    template = loader.get_template('instructor_module/instructor_change_schedule.html')

    context = {
        'test': 'test'
    }
    return HttpResponse(template.render(context,request))  

def view_assignments (request,id):
    """ This function renders the student page """
    acts = Course_Activity.objects.filter(course_batch=id)
    context={
        'acts':acts,
        'id':id,
    }
    # print(acts)
    return render(request, 'instructor_module/view_assignments.html',context)

def add_assignment(request, id):
    if request.method == "POST":
        form = ActivityForms(request.POST)
        
        batch = Course_Enrollment.objects.filter(pk=id).first()
        title = request.POST['activity_title']
        desc=request.POST['activity_desc']
        attachment = request.POST['activity_attachment']
        d1 = request.POST.get('deadline_0')
        d2 = request.POST.get('deadline_1')
        deadline = d1+" "+d2
        date_object = datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        if date_object <= datetime.now():
            return render(request, 'instructor_module/add_assignment.html',{'form':form, 'id': id, 'error_msg': 'Deadline should be in the future'})
        else:
            activity_post = Course_Activity(course_batch = batch,activity_title = title,activity_desc = desc,activity_attachment = attachment,deadline = deadline)
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
        attach = request.POST['attachment']
        end_date = request.POST['d1']
        end_time = request.POST['t1']
        dt = end_date+" "+end_time
        grade = request.POST['gr']

        act.activity_title = title
        act.activity_desc = desc
        act.activity_attachment = attach
        act.deadline = dt
        act.grading_percentage = grade
        act.save(update_fields=['activity_title','activity_desc','activity_attachment','deadline','grading_percentage'])
        return HttpResponseRedirect(reverse('view_assignments', kwargs={'id': id}))
    return render(request, "instructor_module/edit_assignment.html", context)


# def confirm_delete_assignment(request,id):
#     activity =  Course_Activity.objects.get(id=Course_Activity.pk)
#     return render(request, 'instructor_module/confirm_delete_assignment.html',{'activity':activity})

# def approve_delete_assignment(request,id):
#     activity = Course_Activity.objects.get(id=Course_Activity.pk)
#     activity.delete()
#     messages.success(request,'Activity deleted!')
#     return render(request,'instructor_module/view_assignments.html')
