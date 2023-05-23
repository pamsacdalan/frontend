from django.urls import path
from django.contrib import admin
from apps.sitlms_student import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('student_profile', views.student_profile,name="student_profile"),
    path('student_profile/course_details/', views.student_course_details,name="course_details"),
    path('student_profile/edit_profile/', views.student_edit_profile,name="edit_profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)