from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Instructor_Auth, Schedule
from django.urls import reverse
from django.template import loader
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone


list_course_mode = ["Webinar","Onsite","Self-Paced"]
list_frequency = ["Once","Daily","Weekly"]



def course_mode(course_mode):
    
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

def write_schedule(course_batch, start_date, end_date, start_time, 
                   end_time, frequency):

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    if frequency == '1':
        delta = timedelta(days=1) 
    elif frequency == '7':
        delta = timedelta(days=7)
    else:
        delta = timedelta(days=1000)

    
    while (end_date) >= start_date:
        start_date_obj = start_date.date()
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        concatenated_start_datetime = datetime.combine(start_date_obj, start_time_obj)
        concatenated_start_datetime = timezone.make_aware(concatenated_start_datetime, timezone.get_current_timezone())

        end_date_obj = start_date.date()
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        concatenated_end_datetime = datetime.combine(end_date_obj, end_time_obj)
        concatenated_end_datetime = timezone.make_aware(concatenated_end_datetime, timezone.get_current_timezone())

        
        # user_id = User.objects.values_list('id', flat=True).get(first_name=fname, last_name=lname)


        schedule = Schedule(
            start_date = concatenated_start_datetime,
            end_date = concatenated_end_datetime,
            course_batch = Course_Enrollment.objects.get(course_batch=course_batch)
            # user_id = User.objects.get(id=user_id)
            )

        schedule.save()
        start_date += delta



def enrol_course(request):

    template = loader.get_template('admin_module/enrol_course.html')
    option1_course_id = sorted([x['course_title'] for x in Course_Catalog.objects.values('course_title').distinct()], key=str.lower)

    full_name = sorted([' '.join(map(str,x)) for x in zip
                        ([User.objects.values_list('first_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()], 
                        [User.objects.values_list('last_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()])], key=str.lower)
    # option2_instructor_id = sorted([User.objects.values_list('username', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()], key=str.lower)
    
    
    
    
    context = {'option_course_id': option1_course_id,
                'full_name': full_name,
                'course_mode': list_course_mode}
    

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
        # full_name = request.POST['full_name']
        # fname = full_name.split()[0]
        # lname = full_name.split()[-1]      
        # user_id = User.objects.values_list('id', flat=True).get(first_name=fname, last_name=lname)
        # instructor_id = Instructor_Auth.objects.get(user=user_id)

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

        frequency = request.POST['frequency'] # will return 0, 1 or 7
        print(frequency, type(frequency))
       

        enrolled_course = Course_Enrollment(
                course_batch  = course_batch,
                course_id = course_title,
                # instructor_id = instructor_id,
                session_details  = session_details,
                start_date  = start_date,
                end_date  = end_date,
                start_time = start_time,
                end_time = end_time,
                frequency = frequency,
                course_mode  = course_mode)
        enrolled_course.save()

# Convert the date and time strings to datetime objects
        write_schedule(course_batch, start_date, end_date, start_time, 
                   end_time, frequency)

        return redirect('view_enrolled_course')

    
    return HttpResponseRedirect(reverse('enrol_course'))

def edit_enrolled_course(request, id):
    enrolled_course = Course_Enrollment.objects.get(course_batch=id)
    specific_username = enrolled_course.instructor_id
    specific_id = enrolled_course.course_id
    specific_course_mode = course_mode_rev(enrolled_course.course_mode)
    specific_frequency = frequency_rev(enrolled_course.frequency)


    option1_course_id = sorted([x['course_title'] for x in Course_Catalog.objects.values('course_title').distinct()], key=str.lower)
    # option2_instructor_id = sorted([User.objects.values_list('username', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()], key=str.lower)

    full_name = sorted([' '.join(map(str,x)) for x in zip
                        ([User.objects.values_list('first_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()], 
                        [User.objects.values_list('last_name', flat=True).get(id=x['user']) for x in Instructor_Auth.objects.values('user').distinct()])], key=str.lower)

    context = {'enrolled_course':enrolled_course, 
               'option_course_id': option1_course_id,
                'full_name': full_name,
                'sid': specific_id,
                'iid': specific_username,
                'course_mode': list_course_mode,
                'scm': specific_course_mode,
                'lof': list_frequency,  
                'sf': specific_frequency,         
                }

    if request.method == "POST":
        
        course_batch  = request.POST['course_batch']
        course_id = Course_Catalog.objects.get(course_title=request.POST['course_title'])
        # instructor_id = User.objects.values_list('id', flat=True).get(username=request.POST['username'])
        # username = Instructor_Auth.objects.get(user=instructor_id)

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
            frequency='0'
        elif frequency == "Daily":
            frequency='1'
        else:
            frequency='7'

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

        # This is the Schedule Part
        Schedule.objects.filter(course_batch = course_batch).delete()
        write_schedule(course_batch, start_date, end_date, start_time, 
                   end_time, fname, lname, frequency)



        return redirect('view_enrolled_course')
      
    return render(request, "admin_module/edit_enrolled_course.html", context)


def delete_enrolled_course(request,id):
    enrolled_course = Course_Enrollment.objects.get(course_batch=id)
 
    if request.method == "POST":
        enrolled_course.delete()
        Schedule.objects.filter(course_batch = id).delete()
        return redirect('view_enrolled_course')
 
    return render(request, "admin_module/delete_enrolled_course.html")


def add_change_instructor():
    pass

