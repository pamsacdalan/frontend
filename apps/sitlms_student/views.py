from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Student_Enrollment, Students_Auth
from django.template import loader
from datetime import datetime, date, timedelta
# Create your views here.


def student_profile(request):
    
    user = request.user
    query = get_user_model().objects.filter(id=user.id)
    user_id = query.first().id
    student_id = Students_Auth.objects.get(user=user_id)
    student_courses = Student_Enrollment.objects.filter(student_id=student_id).values()
    enrolled_courses = Student_Enrollment.objects.filter(student_id=student_id).count
    # print(student_courses)
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

    

    date_today = date.today()
    dates = [date_today]
    scheduled_course = []

    for i in range(1,7): # next 7 days
        dates.append(date_today + timedelta(days=i))

    for course in course_details:
        intersect = list(set(course['days']) & set(dates))
        if len(intersect) > 0:
            scheduled_course.append(course)
    

    # course frequency
    # 0 = once
    # 1 = daily
    # else = weekly # assumption same day as date start
        
    print(scheduled_course)

    context = {
        'course_enrolled_list':student_courses,
        'stud_id':student_id,
        'course_count':enrolled_courses,
        'scheduled_course':scheduled_course,
        'dates': dates,

                }
    return render(request,'student_module/student.html',context)

def student_view_course(request,id):
    enrolled_class = Student_Enrollment.objects.filter(course_batch=id)
    # print(enrolled_class)
    context={
        'class':enrolled_class,
    }
    return render(request,'student_module/view_courses.html',context)


def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')


def student_edit_profile(request):
    
    """ This function renders the student edit profile"""
    
    return render(request, 'student_module/edit_profile.html')

