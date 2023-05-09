from django.urls import path
from django.contrib import admin
from apps.sitlms_app import views
from .crud import student, instructor, course, sit_admin

urlpatterns = [
    # path('', views.admin_index,name="sit_admin_dashboard"),
    path('',views.home,name="home"),
    path('dashboard/', views.dashboard,name="sit_admin_dashboard"),
    path('registration/reset_pw_email',views.reset_pw_request_success, name="request_reset_pw"),
    path('sit-admin/list', sit_admin.AdminList.as_view(), name="adminlist"),
    path('sit-admin/create', sit_admin.sitadmin_register, name="admincreate"),
    path('sit-admin/update/<id>', sit_admin.sitadmin_update, name="adminupdate"),
    path('sit-admin/delete/<pk>', sit_admin.AdminDelete.as_view(), name="admindelete"),
    path('student/', student.student),
    path('student/view/', student.view_students,name='view_students'),
    path('student/edit/<int:id>', student.edit_student),
    path('student/update/<int:id>', student.update_student),
    path('student/delete/<int:id>', student.delete_student),
    path('student/delete/confirm/<int:id>', student.delete_student, name='delete_student'),
    path('student/update/updaterecord/<int:id>', student.update_record),
    path('student/view/import_csv', views.view_csv, name='view_csv'),
    path('student/view/csv_instruction', views.csv_instruction, name='csv_instruction'),
    path('student/view/csv_instruction/downloadfile', views.downloadfile, name='downloadfile'),
    path('instructor/',instructor.instructor),
    path('instructor/add/',instructor.add_instructor,name='add_instructor'),
    path('instructor/view/',instructor.view_instructors,name='view_instructors'),
    path('instructor/add/add_info/',instructor.add_instructor_info,name='add_instructor_info'),
    path('instructor/delete/<int:id>',instructor.delete_instructor,name='delete_instructor'),
    path('instructor/edit/<int:id>',instructor.edit_instructor,name='edit_instructor'),
    path('course/', course.courses),
    path('course/add_course/', course.add_course, name='add_course'),
    path('course/add_course/add_course_info/', course.add_course_info, name='add_course_info'),
    path('course/view_course/', course.view_course, name='view_course'),
    path('course/edit_course/<int:id>', course.edit_course, name='edit_course'),
    path('course/delete_course/<int:id>', course.delete_course, name='delete_course'),
    path('student_profile', views.student_profile,name="student_profile"),
    path('student_profile/course_details/', views.student_course_details,name="course_details"),
     path('student_profile/edit_profilw/', views.student_edit_profile,name="edit_profile"),
    
]

'''
    path('sit-admin/list', views.AdminList.as_view(), name="adminlist"),
    path('sit-admin/create', views.sitadmin_register, name="admincreate"),
    path('sit-admin/update/<id>', views.sitadmin_update, name="adminupdate"),
    path('sit-admin/delete/<pk>', views.AdminDelete.as_view(), name="admindelete"),
'''



