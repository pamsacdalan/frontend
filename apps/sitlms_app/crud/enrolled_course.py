from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Instructor_Auth, Schedule
from django.urls import reverse
from django.template import loader
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.forms import URLField
from datetime import datetime, time, timedelta
from django.utils import timezone
import json


list_course_mode = ["Webinar","Onsite","Self-Paced"]
list_frequency = ["Once","Daily","Weekly"]



def course_mode(course_mode):
    print("pumasok ako rito")
    if course_mode == "Webinar":
        course_mode=0
    elif course_mode == "Onsite":
        course_mode=1
    else:
        course_mode=2
    return course_mode


def course_mode_rev(course_mode):
    if course_mode == 0 :
        course_mode="Webinar"
    elif course_mode == 1:
        course_mode="Onsite"
    else:
        course_mode="Self-paced"
    return course_mode

def frequency_rev(frequency):
    if frequency == 0 :
        frequency="Once"
    elif frequency == 1:
        frequency="Daily"
    else:
        frequency="Weekly"
    return frequency

def string_to_date(frequencies, start_date, end_date, start_time, end_time, course_batch):
        # print(frequencies, start_date, end_date, start_time, end_time, course_batch, user_id)
        # print(type(frequencies), type(start_date), type(end_date), type(start_time), type(end_time), type(course_batch), type(user_id))
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if frequencies == '1':
            delta = timedelta(days=1) 
        elif frequencies == '7':
            delta = timedelta(days=7)
        else:
            delta = timedelta(days=10000)
            print('error')

        
        while (end_date) >= start_date:
            start_date_obj = start_date.date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()

            schedule = Schedule(
                session_date = start_date_obj,
                start_time = start_time_obj,
                end_time = end_time_obj,
                # end_date = concatenated_end_datetime,
                course_batch = Course_Enrollment.objects.get(course_batch=course_batch),

                )
            schedule.save()
            start_date += delta



def enrol_course(request):

    template = loader.get_template('admin_module/enrol_course.html')
    option1_course_id = sorted([x['course_title'] for x in Course_Catalog.objects.values('course_title').distinct()], key=str.lower)

    full_name = sorted([' '.join(map(str,x)) for x in zip
                        ([User.objects.values_list('first_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()], 
                        [User.objects.values_list('last_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()])], key=str.lower)
    
    
    ####ADDED
    response = get_schedule_data(request)  # Fetch schedule data from the get_schedule_data view
    schedules = json.loads(response.content)  # Parse the JSON data from the response content

    
    #adds fullname in schedules
    #instructor
    for x in schedules:
        inst_id = Course_Enrollment.objects.values_list('instructor_id', flat=True).get(course_batch=x['course_batch'])
        # print("Instructor id", inst_id)
        uid = Instructor_Auth.objects.values_list('user_id', flat=True).get(id=inst_id)
        # print('uid', uid)
        fn = User.objects.values_list('first_name', flat=True).get(id=uid)
        ln = User.objects.values_list('last_name', flat=True).get(id=uid)
        x['fullname'] = fn + " " + ln

    context = {'option_course_id': option1_course_id,
                'full_name': full_name,
                'course_mode': list_course_mode,
                'schedules': json.dumps(schedules)}     #list [{'course_batch': 'Python101', 'user_id': 28, 'start_date': '2023-05-08T01:38:00Z', 'end_date': '2023-05-08T13:39:00Z'}]
    
    return HttpResponse(template.render(context,request))

def view_enrolled_course(request):
    template = loader.get_template('admin_module/view_enrolled_course.html')
    course_enrolled_list = Course_Enrollment.objects.all()
    context = {'course_enrolled_list':course_enrolled_list,
               'option_course_title': [x['course_title'] for x in Course_Catalog.objects.values('course_title').distinct()]
                }
    return HttpResponse(template.render(context,request))

def enrol_course_info(request):
    
    if request.method == "POST":
        course_batch  = request.POST['course_batch']
        course_title = Course_Catalog.objects.get(course_title=request.POST['course_title'])
        full_name = request.POST['full_name']
        fname = full_name.split()[0]
        lname = full_name.split()[-1]      
        user_id = User.objects.values_list('id', flat=True).get(first_name=fname, last_name=lname)
        instructor_id = Instructor_Auth.objects.get(user=user_id)


        session_details  = request.POST['session_details']        
        start_date  = request.POST['start_date']
        end_date  = request.POST['end_date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        course_mode = request.POST['course_mode']
        
        if course_mode == "Webinar":
            course_mode=0
        elif course_mode == "Onsite":
            course_mode=1
        else:
            course_mode=2

        frequencies = request.POST['frequency']
       

        enrolled_course = Course_Enrollment(
                course_batch  = course_batch,
                course_id = course_title,
                instructor_id = instructor_id,
                session_details  = session_details,
                start_date  = start_date,
                end_date  = end_date,
                start_time = start_time,
                end_time = end_time,
                frequency = frequencies,
                course_mode  = course_mode)
        enrolled_course.save()


        string_to_date(frequencies, start_date, end_date, start_time, end_time, course_batch)

        return redirect('view_enrolled_course')

    
    return HttpResponseRedirect(reverse('enrol_course'))

def edit_enrolled_course(request, id):  #id here is the coursebatch (i.e. Python101)
    enrolled_course = Course_Enrollment.objects.get(course_batch=id) #ex: Python101

    specific_username = enrolled_course.instructor_id
    specific_id = enrolled_course.course_id
    specific_course_mode = course_mode_rev(enrolled_course.course_mode)
    specific_frequency = frequency_rev(enrolled_course.frequency)


    option1_course_id = sorted([x['course_title'] for x in Course_Catalog.objects.values('course_title').distinct()], key=str.lower)
    # option2_instructor_id = sorted([User.objects.values_list('username', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()], key=str.lower)

    full_name = sorted([' '.join(map(str,x)) for x in zip
                        ([User.objects.values_list('first_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()], 
                        [User.objects.values_list('last_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()])], key=str.lower)

    response = get_schedule_data_edit(request, id)  # Fetch schedule data from the get_schedule_data view
    schedules = json.loads(response.content)  # Parse the JSON data from the response content
    
    
    #adds fullname in schedules
    for x in schedules:
        inst_id = Course_Enrollment.objects.values_list('instructor_id', flat=True).get(course_batch=x['course_batch'])
        # print("Instructor id", inst_id)
        uid = Instructor_Auth.objects.values_list('user_id', flat=True).get(id=inst_id)
        # print('uid', uid)
        fn = User.objects.values_list('first_name', flat=True).get(id=uid)
        ln = User.objects.values_list('last_name', flat=True).get(id=uid)
        x['fullname'] = fn + " " + ln


    context = {'enrolled_course':enrolled_course, 
               'option_course_id': option1_course_id,
                'full_name': full_name,
                'sid': specific_id,
                'iid': specific_username,
                'course_mode': list_course_mode,
                'scm': specific_course_mode,
                'lof': list_frequency,  
                'sf': specific_frequency,  
                'schedules' : json.dumps(schedules)       
                }

    if request.method == "POST":
        course_batch  = request.POST['course_batch']
        course_id = Course_Catalog.objects.get(course_title=request.POST['course_title'])
        full_name = request.POST['full_name']
        fname = full_name.split()[0]
        lname = full_name.split()[-1]      
        user_id = User.objects.values_list('id', flat=True).get(first_name=fname, last_name=lname)
        instructor_id = Instructor_Auth.objects.get(user=user_id)
        session_details  = request.POST['session_details']  
        start_date  = request.POST['start_date']
        end_date  = request.POST['end_date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        course_mode  = request.POST['course_mode']
        if course_mode == "Webinar":
            course_mode=0
        elif course_mode == "Onsite":
            course_mode=1
        else:
            course_mode=2

        frequency = request.POST['frequency']
        if frequency == "Once":
            frequency=0
        elif frequency == "Daily":
            frequency=1
        else:
            frequency=7



        enrolled_course.course_batch = course_batch
        enrolled_course.course_id = course_id
        enrolled_course.instructor_id = instructor_id
        enrolled_course.session_details = session_details
        enrolled_course.start_date =start_date
        enrolled_course.end_date = end_date
        enrolled_course.course_mode = course_mode
        enrolled_course.start_time = start_time
        enrolled_course.end_time = end_time
        enrolled_course.frequency = frequency
        enrolled_course.save()


        #DELETES THE RECORD IN SCHEDULED TABLE, THEN SAVE ANOTHER RECORD
        scheduled_course = list(Schedule.objects.filter(**{'course_batch':id}).values()) #gets each entry of the argument id from schedule table
    
        for record in scheduled_course:
            deleted_scheduled_course = Schedule.objects.get(schedule_id=record['schedule_id'])
            deleted_scheduled_course.delete()
        
        string_to_date(str(frequency), start_date, end_date, start_time, end_time, course_batch)

        return redirect('view_enrolled_course')
    
    return render(request, "admin_module/edit_enrolled_course.html", context)


def delete_enrolled_course(request,id):
    enrolled_course = Course_Enrollment.objects.get(course_batch=id)
 
    if request.method == "POST":
        enrolled_course.delete()
        return redirect('view_enrolled_course')
    return render(request, "admin_module/delete_enrolled_course.html")


def get_schedule_data(request):
    schedules = Schedule.objects.all().values('course_batch', 'session_date', 'start_time', 'end_time')  # Query the necessary fields from the Schedule model
    data = list(schedules)  # Convert QuerySet to list of dictionaries
    return JsonResponse(data, safe=False)


def get_schedule_data_edit(request,id):
    schedules = Schedule.objects.all().values('course_batch', 'session_date', 'start_time', 'end_time')  # Query the necessary fields from the Schedule model
    data = list(schedules)  # Convert QuerySet to list of dictionaries
    list_course_batches = [x['course_batch'] for x in data] 
    new_data = [row for row in data if row['course_batch'] !=id]
    return JsonResponse(new_data, safe=False)   