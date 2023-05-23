from django.urls import path
from django.contrib import admin
from apps.sitlms_student import views




urlpatterns = [
    path('student_profile', views.student_profile,name="student_profile"),
    path('student_profile/course_details/', views.student_course_details,name="course_details"),
    path('student_profile/edit_profile/', views.student_edit_profile,name="edit_profile"),
    path('student_profile/view_courses/<str:id>', views.student_view_course, name='view_courses'),
    path('student-no-access',views.custom_403_2,name="student-no-access"),
]
