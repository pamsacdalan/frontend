from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from apps.sitlms_app.models import Program
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from apps.sitlms_app.crud.access_test import is_admin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# CRUD for Program
@user_passes_test(is_admin)
def view(request):
    template = loader.get_template('admin_module/view_program.html')
    programs = Program.objects.all().order_by('program_code')

    # for pagination
    page = request.GET.get('page', 1) # default page (default to first page)
        
    items_per_page = 5
    paginator = Paginator(programs, items_per_page)
    try:
            programs_page = paginator.page(page)
    except PageNotAnInteger:
            programs_page = paginator.page(1)
    except EmptyPage:
            programs_page = paginator.page(paginator.num_pages)
                
    context = {'programs_page':programs_page, 'programs': programs}
    return HttpResponse(template.render(context,request))


@user_passes_test(is_admin)
def add(request):
    template = loader.get_template('admin_module/add_program.html')

    if request.method == "POST":
        program_code = request.POST['program_code']
        program_title = request.POST['program_title']

        # id not auto field, temp solution
        last_program_id = getattr(Program.objects.last(), 'program_id')

        program = Program(program_id=last_program_id + 1, program_code=program_code, program_title=program_title)
        program.save()

        return redirect('view_program')

    return HttpResponse(template.render({},request))

@user_passes_test(is_admin)
def edit(request,id):
    program = Program.objects.get(program_id=id)
    context = {
        'program':program
    }

    if request.method == "POST":
        program_code = request.POST['program_code']
        program_title = request.POST['program_title']

        program.program_code = program_code
        program.program_title = program_title 

        program.save(update_fields=['program_code','program_title'])

        return redirect('view_program')

    return render(request, "admin_module/edit_program.html", context)

@user_passes_test(is_admin)
def delete(request,id):
    program = Program.objects.get(program_id=id)

    if request.method == "POST":
        program.delete()
        return redirect('view_program')

    return render(request, "admin_module/delete_program.html")