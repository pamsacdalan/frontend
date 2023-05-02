from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from apps.sitlms_app.models import Course_Catalog
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from apps.sitlms_app.forms import  CourseForm


# CRUD for Courses

def courses(request):
        return render(request, 'admin_module/courses.html')

def add_course(request):
        form = CourseForm(request.POST or None)
        template = loader.get_template('admin_module/add_course.html')
        context = {
                'form': form,
                'page_title': 'Add Course'
        }
        if request.method == 'POST':
                if form.is_valid():
                        name = form.cleaned_data.get('course_title')
                        description = form.cleaned_data.get('course_desc')
                        try:
                                course = Course_Catalog()
                                course.course_title = name
                                course.course_desc = description
                                course.save()
                                messages.success(request, "Course Souccessfully Added")
                                return redirect('/course')
                        except:
                                messages.error(request, "Could Not Add Course")
                else:
                        messages.error(request, "Could Not Add Course")
        #return HttpResponse(template.render({},request, context))
        return render(request, 'admin_module/add_course.html', context)


def add_course_info(request):
        course_desc = request.POST['course_desc']
        course_title = request.POST['course_title']
        course = Course_Catalog(course_desc=course_desc, course_title=course_title)
        course.save()
        return HttpResponseRedirect('/sit-admin/course/view_course')


def view_course(request):
        template = loader.get_template('admin_module/view_course.html')
        course_list = Course_Catalog.objects.all()
        context = {'course_list':course_list}
        return HttpResponse(template.render(context,request))


def edit_course(request, id):
        course = Course_Catalog.objects.get(course_id=id)
        context = {'course': course}


        if request.method == "POST":
                course_desc = request.POST['course_desc']
                course_title = request.POST['course_title']

                course.course_desc = course_desc
                course.course_title = course_title

                course.save(update_fields=['course_desc', 'course_title'])

                return HttpResponseRedirect(reverse('view_course'))

        return render(request, "admin_module/update_course.html", context)



def delete_course(request, id):
        course = Course_Catalog.objects.get(course_id=id)

        if request.method == 'POST':
                course.delete()
                return HttpResponseRedirect(reverse('view_course'))

        return render(request, 'admin_module/delete_course.html')
