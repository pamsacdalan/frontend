from django.shortcuts import render

# Create your views here.


def student_profile(request):
    
    """ This function renders the student page """
    
    return render(request, 'student_module/student.html')

def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')


def student_edit_profile(request):
    
    """ This function renders the student edit profile"""
    
    return render(request, 'student_module/edit_profile.html')