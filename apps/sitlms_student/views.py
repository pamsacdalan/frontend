from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Student_Enrollment, Students_Auth, Instructor_Auth, Program
from apps.sitlms_instructor.models import Course_Announcement
from operator import itemgetter
# Create your views here.


def student_profile(request):
    
    user = request.user
    query = get_user_model().objects.filter(id=user.id)
    user_id = query.first().id
    student_id = Students_Auth.objects.get(user=user_id)
    courses = Student_Enrollment.objects.filter(student_id=student_id).values()
    enrolled_courses = Student_Enrollment.objects.filter(student_id=student_id).count
    context = {
        'course_enrolled_list':courses,
        'stud_id':student_id,
        'course_count':enrolled_courses,
             }
    return render(request,'student_module/student.html',context)

def student_view_course(request,id):

    """This function displays the announcements, students, and additional information per course enrolled of the user"""

    course_batch = id
    user = request.user
    query = get_user_model().objects.filter(id=user.id)
    user_id = query.first().id

    """Details for Announcement Section"""
    announcement_details = Course_Announcement.objects.filter(course_batch = id).order_by("-date_posted").values()

    """Details for Course Info Section"""
    course_details = Course_Enrollment.objects.filter(course_batch=id).values()
    instructor_id = course_details[0]['instructor_id_id']
    instructor_details = Instructor_Auth.objects.get(id=instructor_id)
    instructor_name = f"{instructor_details.user.first_name} {instructor_details.user.last_name}"
    

  
    """Details for Classmates Section"""
    student_ids_enrolled = Student_Enrollment.objects.values_list('student_id').filter(course_batch=id)
    student_details = Students_Auth.objects.filter(id__in=student_ids_enrolled).exclude(user_id=user_id).values().order_by('id')
    program_ids = student_details.values_list('program_id_id')
    program_code = Program.objects.filter(program_id__in=program_ids).values()

    count = len(student_details)
    complete_student_details = list()
    for x in range(count):
        for program in program_code:
            if student_details[x]['program_id_id'] == program['program_id']:
                name = Students_Auth.objects.get(id=student_details[x]['id'])
                student_full_name = {'full_name':f"{name.user.first_name} {name.user.last_name}", 'last_name':name.user.last_name}
                complete_student_details.append({**student_details[x], **program, **student_full_name})

    complete_student_details = sorted(complete_student_details, key=itemgetter('last_name'))

    context={
        'course_batch': course_batch,
        'announcement_details':announcement_details,
        'course_details':course_details,
        'classmate_details':complete_student_details,
        'instructor_name':instructor_name,

    }
    return render(request,'student_module/view_courses.html',context)


def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')


def student_edit_profile(request):
    
    """ This function renders the student edit profile"""
    
    return render(request, 'student_module/edit_profile.html')



