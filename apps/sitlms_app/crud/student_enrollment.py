from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Students_Auth, Student_Enrollment, Program, Schedule
from django.urls import reverse
from django.template import loader
from django.contrib.auth.models import User
from datetime import date
import json
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_app.crud.access_test import is_admin
from datetime import date, datetime ,timedelta
from django.db.models import Max
from datetimerange import DateTimeRange
from operator import itemgetter


def get_redundant_schedule(course_batch):
    """
    return a list of all courses that have redundant schedule with the course to be enrolled
    """

    date_past24weeks = date.today() - timedelta(weeks=24)
    schedule_exclude_past6months = Schedule.objects.values('course_batch_id').annotate(max_date=Max('session_date')).filter(session_date__gte=date_past24weeks) #tocheck
    possible_courses =  [x['course_batch_id'] for x in schedule_exclude_past6months]

    if course_batch in possible_courses:
        possible_courses.remove(course_batch)

    redundant_courses = [] #contain all courses that have redundant schedule with the given course

    for course in possible_courses:
        all_session = Schedule.objects.filter(course_batch_id=course).values()
        for session in all_session:
            #looping all session of the possible reduntant courses
            occurences = Schedule.objects.filter(course_batch_id=course_batch).values()
            for occurence in occurences:
                #looping all session of the course to be enrolled

                if session["session_date"] == occurence["session_date"]: #checks if the possible_reduntant_course's session date is equal to course_to_be_enrolled's session date

                #concat session date with start and end time
                    
                    session_start = datetime.combine(session["session_date"], session["start_time"]).strftime('%Y-%m-%d %H:%M:%S')
                    session_end = datetime.combine(session["session_date"], session["end_time"]).strftime('%Y-%m-%d %H:%M:%S')
                    #concat occurence date to start and end time
                    occurence_start = datetime.combine(occurence["session_date"], occurence["start_time"]).strftime('%Y-%m-%d %H:%M:%S')
                    occurence_end = datetime.combine(occurence["session_date"], occurence["end_time"]).strftime('%Y-%m-%d %H:%M:%S')
                    session_time_range = DateTimeRange(session_start, session_end)
                    occurence_time_range = DateTimeRange(occurence_start, occurence_end)
                    if session_time_range.is_intersection(occurence_time_range): 
                        redundant_courses.append(course)
                        break
            if course in redundant_courses:
                break   
            
    redundant_courses.append(course_batch)
    return redundant_courses

@user_passes_test(is_admin)
def enroll_student(request, id):
    ''' enroll one or more selected students '''

    template = loader.get_template('admin_module/enroll_student.html')
    student_available = Student_Enrollment.objects.values_list('student_id').filter(course_batch__in=get_redundant_schedule(id)).distinct()
    students = Students_Auth.objects.exclude(id__in=student_available).filter(active_deactive=True).values()  # can enroll only all active students
    student_list = students.values().order_by('user_id')
    student_ids = student_list.values_list('user_id')
    student_details = User.objects.filter(id__in=student_ids).values().order_by('id')

    program_ids = students.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values()  # program code to be added to new_list

    count = len(student_ids)

    # pass list of program code as context for a dropdown on frontend
    programs = []
    program_code_list = program_code.values().order_by('program_code').values_list('program_code')

    for j in program_code_list:
        programs.append(j[0])

    programs.insert(0,'All')

    # create a new list to pass as context
    new_list = []

    # remove this column from User to avoid confusion
    for i in student_details:
        i.pop('id')

    # add the key-value pair of Student_Auth and User to the list
    for x in range(count):
        for program in program_code:
            if student_list[x]['program_id_id'] == program['program_id']:
                new_list.append({**student_list[x], **student_details[x], **program})

    ## Sort list to be by program code
    new_list = sorted(new_list, key=itemgetter('program_code'))

    context = {'student_list': new_list, 'id': id, 'programs':programs}

    if request.method == "POST":
        id_list = request.POST.getlist('checks[]')
        for item in id_list:
            enrollment = Student_Enrollment(
                student_id=Students_Auth.objects.get(user_id=item),
                course_batch=Course_Enrollment.objects.get(course_batch=id),
                grades='TBD',
                date_enrolled=date.today())

            enrollment.save()
        print(f'{id_list} id list')
        return redirect('view_enrolled_course')



    return HttpResponse(template.render(context, request))

@user_passes_test(is_admin)
def view_enrolled_students(request, id):


    ''' view all enrolled students per course '''
    template = loader.get_template('admin_module/view_enrolled_students.html')
    course = Course_Enrollment.objects.get(course_batch=id)
    students = Student_Enrollment.objects.filter(course_batch=id).values()
    student_list = students.values().order_by('student_id_id')
    student_ids = student_list.values_list('student_id')
    student_auth_details = Students_Auth.objects.filter(id__in=student_ids).values().order_by('user_id')
    user_ids = student_auth_details.values_list('user_id')
    student_details = User.objects.filter(id__in=user_ids).values().order_by('id')

    program_ids = student_auth_details.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values()  # program code to be added to new_list

    count = len(student_ids)

    # create a new list to pass as context
    new_list = []

    for l in student_details:
        l.pop('id')

    for x in range(count):
        for program in program_code:
            if student_auth_details[x]['program_id_id'] == program['program_id']:
                new_list.append({**student_auth_details[x], **student_details[x], **student_list[x], **program})

    ## Sort list to be by program code
    new_list = sorted(new_list, key=itemgetter('program_code'))

    context = {
        'course': course,
        'option_course_title': [x['course_title'] for x in Course_Catalog.objects.values('course_title').distinct()],
        'students': new_list,
    }

    return HttpResponse(template.render(context, request))

@user_passes_test(is_admin)
def delete_enrollment(request, course_batch, enrollment_id):
    "function to unenroll a student from a course"
    enrollment = Student_Enrollment.objects.get(enrollment_id=enrollment_id)

    if request.method == "POST":
        enrollment.delete()
        return HttpResponseRedirect(reverse('view_enroll_students', kwargs={'id': course_batch}))

    return render(request, "admin_module/delete_student_enrollment.html", {'course_batch': course_batch})

@user_passes_test(is_admin)
def edit_enrollment(request, course_batch, enrollment_id):
    "function to edit grade and status of enrolled student for a certain course"
    status = ["Ongoing", "Completed"]
    enroll_id = Student_Enrollment.objects.filter(
        enrollment_id=enrollment_id).values()  # get the queryset for enrollment_id
    enrollment = Student_Enrollment.objects.get(
        enrollment_id=enrollment_id)  # instantiate from Student_Enrollment model
    student = Students_Auth.objects.get(id=enroll_id[0]['student_id_id'])
    context = {'enrollment': enrollment, 'student': student, 'course_batch': course_batch, "status": status}

    if request.method == "POST":
        grade = request.POST['grade']
        status = request.POST['status']

        enrollment.grades = grade
        enrollment.status = status

        enrollment.save(update_fields=['grades', 'status'])

        return HttpResponseRedirect(reverse('view_enroll_students', kwargs={'id': course_batch}))

    return render(request, "admin_module/edit_student_enrollment.html", context)




