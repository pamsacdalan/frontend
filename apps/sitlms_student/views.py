from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from apps.sitlms_app.models import Course_Catalog, Course_Enrollment, Program, Student_Enrollment, Students, Students_Auth
from django.template import loader

from apps.sitlms_instructor.models import Activity_Comments, Course_Activity
# Create your views here.


def student_profile(request):
    
    user = request.user
    query = get_user_model().objects.filter(id=user.id)
    user_id = query.first().id
    student_id = Students_Auth.objects.get(user=user_id)
    courses = Student_Enrollment.objects.filter(student_id=student_id).values()
    enrolled_courses = Student_Enrollment.objects.filter(student_id=student_id).count
    student_program = Program.to_desc(student_id.program_id)
    # print(courses)
    context = {
        'course_enrolled_list':courses,
        'stud_id':student_id,
        'course_count':enrolled_courses,
        'program':student_program,
                }
    return render(request,'student_module/student.html',context)

def student_view_course(request,id):
    enrolled_class = Student_Enrollment.objects.filter(course_batch=id)
    # print(enrolled_class)
    class_details = Course_Activity.objects.filter(course_batch=id)
    context={
        'class':enrolled_class,
        'details':class_details,
        'id':id,
    }
    return render(request,'student_module/view_courses.html',context)

def student_edit_profile(request):
    
    """ This function renders the student edit profile"""
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
    return render(request, 'student_module/edit_profile.html',context)

def student_view_assignment_details(request, id, pk):
    user = request.user
    batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=pk)
    comment_items = Activity_Comments.objects.filter(course_activity=activity).order_by('timestamp')
    file_relative_url = activity.activity_attachment.url 

    file_url = request.build_absolute_uri(file_relative_url)

    context = {
        'batch':batch,
        'act':activity,
        'cmt':comment_items,
        'file_url':file_url,
        'user':user,
             }
    if request.method == "POST":
        msg = request.POST['msg_area']
        user = request.user
        comment = Activity_Comments(course_activity = activity, uid = user,content = msg)
        comment.save()
        return redirect('student_view_assignment_details',id=id,pk=pk)
    
    return render(request, 'student_module/assignment_details.html',context)

def download_activity_attachment(request, id):
    # batch = Course_Enrollment.objects.get(pk=id)
    activity = Course_Activity.objects.get(id=id) # Retrieve the object with the uploaded file

    # Perform any necessary checks or validations here

    # Retrieve the file path or file object from the model and open it
    file_path = activity.activity_attachment.path
    # print(file_path)
    file = open(file_path, 'rb')

    # Set the appropriate response headers
    filename=str(activity.activity_attachment.name).split('/')[-1]
    response = HttpResponse(file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')
