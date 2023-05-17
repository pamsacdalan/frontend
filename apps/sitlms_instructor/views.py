from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from apps.sitlms_app.models import *
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from apps.sitlms_app.crud.enrolled_course import string_to_date, frequency_rev
from datetime import datetime
import csv




# Create your views here.


def instructor(request):
    
    """ This function renders the student page """
    
    return render(request, 'instructor_module/instructor.html')


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
                # print(value['course_title'])
    
    # print(course_enrolled)

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

    # print(new_list)


    context = {'new_list': new_list,
               'id':id
                }
    
    return HttpResponse(template.render(context,request))  


def change_schedule(request, id): #need notif na nasend na yung request.. helllppp
    # template = loader.get_template('instructor_module/instructor_change_schedule.html')
    enrolled_course = Course_Enrollment.objects.get(course_batch=id) #ex: Python101
    course_batch = enrolled_course.course_batch
    # course_id = enrolled_course.course_id
    # instructor_id = enrolled_course.instructor_id
    # session_details = enrolled_course.session_details 
    # course_mode = enrolled_course.course_mode 
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

        # enrolled_course.course_batch = course_batch
        # enrolled_course.start_date =start_date
        # enrolled_course.end_date = end_date
        # enrolled_course.start_time = start_time
        # enrolled_course.end_time = end_time
        # enrolled_course.frequency = frequency
        # enrolled_course.save()      



        #DELETES THE RECORD IN SCHEDULED TABLE, THEN SAVE ANOTHER RECORD
        # scheduled_course = list(Schedule.objects.filter(**{'course_batch':course_batch}).values()) #gets each entry of the argument id from schedule table

        # for record in scheduled_course:
        #     deleted_scheduled_course = Schedule.objects.get(schedule_id=record['schedule_id'])
        #     deleted_scheduled_course.delete()
        
        # string_to_date(str(frequency), start_date, end_date, start_time, end_time, course_batch)  

        return redirect('view_courses')   
    
    return render(request, "instructor_module/instructor_change_schedule.html", context)


def view_pending_requests(request):
    template = loader.get_template('instructor_module/instructor_view_pending_requests.html')
    pending_requests = Change_Schedule.objects.filter(status='Pending').values()
    context = {'pending_requests':pending_requests}
    return HttpResponse(template.render(context,request))

def cancel_request(request, id):
    schedule = Change_Schedule.objects.filter(id=id)
    schedule.update(status='Cancelled', approval_date = datetime.now() )

    return redirect('/sit-instructor/instructor/view_courses/view_pending_requests/')


def export_csv(request, id):
    students = Student_Enrollment.objects.filter(course_batch=id).values('student_id_id')
    student_auth_details = Students_Auth.objects.filter(id__in=students).values('user_id', 'middlename', 'program_id_id').order_by('user_id')
    user_ids = student_auth_details.values_list('user_id')
    student_details = User.objects.filter(id__in=user_ids).values('first_name', 'last_name', 'username', 'id').order_by('id')
    
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
    
