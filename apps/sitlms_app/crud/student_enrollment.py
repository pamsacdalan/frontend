from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Students_Auth, Student_Enrollment, Program, Schedule
from django.urls import reverse
from django.template import loader
from django.contrib.auth.models import User
from datetime import date
import json


def enroll_student(request, id):
    ''' enroll one or more selected students '''

    template = loader.get_template('admin_module/enroll_student.html')
    student_available = Student_Enrollment.objects.values_list('student_id').filter(course_batch=id).distinct()
    students = Students_Auth.objects.exclude(id__in=student_available).filter(active_deactive="Active").values()  # can enroll only all active students
    student_list = students.values().order_by('user_id')
    student_ids = student_list.values_list('user_id')
    student_details = User.objects.filter(id__in=student_ids).values().order_by('id')

    program_ids = students.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values()  # program code to be added to new_list

    count = len(student_ids)

    # create a new list to pass as context
    new_list = []

    # remove this column from User to avoid confusion
    for i in student_details:
        i.pop('id')

    # add the key-value pair of Student_Auth and User to the list
    # for x in range(count):
    #     new_list.append({**student_list[x],**student_details[x], **program_code[x]})

    for x in range(count):
        for program in program_code:
            if student_list[x]['program_id_id'] == program['program_id']:
                new_list.append({**student_list[x], **student_details[x], **program})

        response = get_schedule_data(request)  # Fetch schedule data from the get_schedule_data view
        schedules = json.loads(response.content)  # Parse the JSON data from the response content
        schedules = json.dumps(schedules)  #should be list
        print("afdcafsdafswafdgagfg")
        print(schedules)





    context = {'student_list': new_list, 'id': id}

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

    context = {
        'course': course,
        'option_course_title': [x['course_title'] for x in Course_Catalog.objects.values('course_title').distinct()],
        'students': new_list,
    }

    return HttpResponse(template.render(context, request))


def delete_enrollment(request, course_batch, enrollment_id):
    "function to unenroll a student from a course"
    enrollment = Student_Enrollment.objects.get(enrollment_id=enrollment_id)

    if request.method == "POST":
        enrollment.delete()
        return HttpResponseRedirect(reverse('view_enroll_students', kwargs={'id': course_batch}))

    return render(request, "admin_module/delete_student_enrollment.html", {'course_batch': course_batch})


def edit_enrollment(request, course_batch, enrollment_id):
    "function to edit grade and status of enrolled student for a certain course"
    enroll_id = Student_Enrollment.objects.filter(
        enrollment_id=enrollment_id).values()  # get the queryset for enrollment_id
    enrollment = Student_Enrollment.objects.get(
        enrollment_id=enrollment_id)  # instantiate from Student_Enrollment model
    student = Students_Auth.objects.get(id=enroll_id[0]['student_id_id'])
    context = {'enrollment': enrollment, 'student': student, 'course_batch': course_batch}

    if request.method == "POST":
        grade = request.POST['grade']
        status = request.POST['status']

        enrollment.grades = grade
        enrollment.status = status

        enrollment.save(update_fields=['grades', 'status'])

        return HttpResponseRedirect(reverse('view_enroll_students', kwargs={'id': course_batch}))

    return render(request, "admin_module/edit_student_enrollment.html", context)





def get_schedule_data(request):
    schedules = Schedule.objects.all().values('course_batch', 'user_id', 'session_date', 'start_time', 'end_time')  # Query the necessary fields from the Schedule model
    data = list(schedules)  # data may contain the schedule of instructor and students
    '''This filters the students schedule'''
    new_data = []
    students_id = list(Students_Auth.objects.all().values_list('user_id', flat=True))   #gets all the user id present in instructorAuth
    print(students_id)

    for x in data:
        if x['user_id'] in students_id:
            new_data.append(x)
            
    return JsonResponse(new_data, safe=False)


def get_schedule_data_edit(request,id):
    schedules = Schedule.objects.all().values('course_batch', 'user_id', 'session_date', 'start_time', 'end_time')  # Query the necessary fields from the Schedule model
    data = list(schedules)  # Convert QuerySet to list of dictionaries
    for x in data:
        if x["course_batch"]==id:
            data.remove(x)
    return JsonResponse(data, safe=False)