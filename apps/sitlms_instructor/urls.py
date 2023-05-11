from django.urls import path
from django.contrib import admin
from apps.sitlms_instructor import views




urlpatterns = [
    path('instructor', views.instructor,name="instructor"),
   
]