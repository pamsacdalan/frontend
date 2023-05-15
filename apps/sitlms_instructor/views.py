from django.shortcuts import render
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Instructor_Auth, Student_Enrollment, Students_Auth, Program
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import get_user_model




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

