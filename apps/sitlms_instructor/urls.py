from django.urls import path
from django.contrib import admin
from apps.sitlms_instructor import views




urlpatterns = [
    path('instructor', views.instructor,name="instructor"),
    path('instructor/view_courses', views.instructor_view_enrolled_course, name='view_courses'),
   
]