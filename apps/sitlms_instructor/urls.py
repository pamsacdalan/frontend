from django.urls import path
from django.contrib import admin
from apps.sitlms_instructor import views




urlpatterns = [
    path('instructor', views.instructor,name="instructor"),
    path('program/view/',views.post_activity,name="revert"),
    path('instructor/view_courses', views.instructor_view_enrolled_course, name='view_courses'),
    path('instructor/view_students/<str:id>', views.view_students, name='view_students'),
    path('instructor/view_courses/request_for_change_schedule/<str:id>', views.change_schedule, name='change_schedule'),
    path('instructor/view_courses/<str:id>/assignments', views.view_assignments, name='view_assignments'),
    path('instructor/view_courses/<str:id>/assignments/add', views.add_assignment, name='add_assignment'),
    path('instructor/view_courses/<str:id>/assignments/edit/<int:pk>', views.update_assignment, name='update_assignment'),
    path('instructor/course/<str:id>', views.instructor_course, name='view_instructor_course'),
    path('instructor/course/<str:id>/create_announcement', views.create_announcement, name='create_announcement'),
    path('instructor/course/<str:course_batch>/remove_announcement/<int:schedule_id>', views.remove_announcement, name='delete_announcement'),
    path('instructor/course/<str:course_batch>/edit_announcement/<int:schedule_id>', views.edit_announcement, name='edit_announcement'),
]
   
