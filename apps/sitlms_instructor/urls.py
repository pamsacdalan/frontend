from django.urls import path
from django.contrib import admin
from apps.sitlms_instructor import views




urlpatterns = [
    path('instructor', views.instructor,name="instructor"),
    path('instructor/view_courses', views.instructor_view_enrolled_course, name='view_courses'),
    path('instructor/view_courses/<str:id>', views.view_students, name='view_students'),
    path('instructor/view_courses/request_for_change_schedule/<str:id>', views.change_schedule, name='change_schedule')
   
]