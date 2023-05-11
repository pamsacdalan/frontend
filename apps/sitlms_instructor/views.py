from django.shortcuts import render

# Create your views here.


def instructor(request):
    
    """ This function renders the student page """
    
    return render(request, 'instructor_module/instructor.html')