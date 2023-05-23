from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Student_Enrollment, Students_Auth
from django.template import loader
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
# Create your views here.

def is_student(user):
    try:
        if hasattr(user,'students_auth'):
            return True
        raise PermissionDenied
    except Exception as e:
        raise PermissionDenied
    
def is_correct_student_cbatch_id(student, cbatch_id):
    try:
        # print(student)
        # print(Student_Enrollment.objects.filter(course_batch=cbatch_id).values('student_id'))
        # print('-')
        if Student_Enrollment.objects.filter(course_batch=cbatch_id, student_id=student).exists():
            pass
        else:
            return True
    except Exception as e:
        return True

@user_passes_test(is_student)   
def custom_403_2(request):
    # Pag pinasa ko with status=403, ayaw magload ng page :(
    # Dapat ganito: render(request, 'custom_403_1.html', status=403)
    return render(request, 'custom_403_2.html')

@user_passes_test(is_student)   
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

@user_passes_test(is_student)   
def student_view_course(request,id):
    if is_correct_student_cbatch_id(request.user.students_auth, id):
        return redirect("student-no-access")
    enrolled_class = Student_Enrollment.objects.filter(course_batch=id)
    # print(enrolled_class)
    context={
        'class':enrolled_class,
    }
    return render(request,'student_module/view_courses.html',context)

@user_passes_test(is_student)   
def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')

@user_passes_test(is_student)   
def student_edit_profile(request):
    
    """ This function renders the student edit profile"""
    
    return render(request, 'student_module/edit_profile.html')

