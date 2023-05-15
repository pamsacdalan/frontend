from django.shortcuts import render
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Instructor_Auth, Schedule
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
