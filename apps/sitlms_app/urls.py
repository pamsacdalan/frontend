from django.urls import path
from django.contrib import admin
from apps.sitlms_app import views
from .crud import student, instructor, course, sit_admin, enrolled_course, student_enrollment, program

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
    path('course_enrollment/', enrolled_course.enrol_course, name='course_enrollment'),
    path('course_enrollment/enrol_course_info/', enrolled_course.enrol_course_info, name='enrol_course_info'),
    path('course_enrollment/view_enrolled_course/', enrolled_course.view_enrolled_course, name='view_enrolled_course'),
    path('course_enrollment/edit_enrolled_course/<str:id>', enrolled_course.edit_enrolled_course, name='edit_enrolled_course'),
    path('course_enrollment/delete_enrolled_course/<str:id>', enrolled_course.delete_enrolled_course, name='delete_enrolled_course'),
    path('course_enrollment/add_or_change_instructor', enrolled_course.add_change_instructor, name='add_or_change_instructor'),
    path('course_enrollment/enroll_student/<str:id>', student_enrollment.enroll_student, name='enroll_student'),
    path('course_enrollment/<str:id>/view_students', student_enrollment.view_enrolled_students, name='view_enroll_students'),
    path('course_enrollment/<str:course_batch>/delete_enrollment/<str:enrollment_id>', student_enrollment.delete_enrollment, name='delete_enrollment'),
    path('course_enrollment/<str:course_batch>/edit_enrollment/<int:enrollment_id>', student_enrollment.edit_enrollment, name='edit_enrollment'),
    path('program/view/',program.view,name="view_program"),
    path('program/add/',program.add,name="add_program"),
    path('program/edit/<int:id>',program.edit,name="edit_program"),
    path('program/delete/<int:id>',program.delete,name="delete_program"),
    

   
    
]

'''
    path('sit-admin/list', views.AdminList.as_view(), name="adminlist"),
    path('sit-admin/create', views.sitadmin_register, name="admincreate"),
    path('sit-admin/update/<id>', views.sitadmin_update, name="adminupdate"),
    path('sit-admin/delete/<pk>', views.AdminDelete.as_view(), name="admindelete"),
'''



