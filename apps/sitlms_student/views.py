from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Student_Enrollment, Students_Auth
from django.template import loader
# Create your views here.


def student_profile(request):
    
    user = request.user
    query = get_user_model().objects.filter(id=user.id)
    user_id = query.first().id
    student_id = Students_Auth.objects.get(user=user_id)
    courses = Student_Enrollment.objects.filter(student_id=student_id).values()
    enrolled_courses = Student_Enrollment.objects.filter(student_id=student_id).count
    print(courses)
    context = {
        'course_enrolled_list':courses,
        'stud_id':student_id,
        'course_count':enrolled_courses,

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

