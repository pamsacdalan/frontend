from django.urls import path
from django.contrib import admin
from apps.sitlms_instructor import views




urlpatterns = [
    path('instructor', views.instructor,name="instructor"),
    path('program/view/',views.post_activity,name="revert"),
    path('instructor/view_report_issues', views.view_report_issues, name='view_report_issues'),
    path('instructor/report_issues', views.report_issues, name='report_issues'),
    path('instructor/view_courses', views.instructor_view_enrolled_course, name='view_courses'),
    path('instructor/view_students/<str:id>', views.view_students, name='view_students'),
    path('instructor/view_courses/request_for_change_schedule/<str:id>', views.change_schedule, name='change_schedule'),
    path('instructor/view_courses/<str:id>/assignments', views.view_assignments, name='view_assignments'),
    path('instructor/view_courses/<str:id>/assignments/add', views.add_assignment, name='add_assignment'),
    path('instructor/view_courses/<str:id>/assignments/edit/<int:pk>', views.update_assignment, name='update_assignment'),
    path('instructor/view_courses/<str:id>/assignments/delete/<int:pk>', views.delete_assignment, name='delete_assignment'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>', views.activity_comments, name='activity_comments'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/download-attachment', views.download_activity_attachment, name='download_activity_attachment'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/edit/<int:fk>', views.edit_comments, name='edit_comments'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/delete/<int:fk>', views.delete_comments, name='delete_comments'),
    path('instructor/course/<str:id>', views.instructor_course, name='view_instructor_course'),
    path('instructor/course/<str:id>/create_announcement', views.create_announcement, name='create_announcement'),
    path('instructor/course/<str:course_batch>/remove_announcement/<int:schedule_id>', views.remove_announcement, name='delete_announcement'),
    path('instructor/course/<str:course_batch>/edit_announcement/<int:schedule_id>', views.edit_announcement, name='edit_announcement'),
    path('instructor/view_courses/view_pending_requests/', views.view_pending_requests, name = 'view_pending_requests'),
    path('instructor/view_courses/view_pending_requests/<int:id>', views.read_notif, name="read_notif"),
    path('instructor/view_courses/view_pending_requests/cancel/<int:id>', views.cancel_request, name='cancel_request'),
    path('instructor/view_courses/<str:id>/', views.export_csv, name='export_csv'),
    path('instructor-no-access',views.custom_403_1,name="instructor-no-access"),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/student_work', views.student_work, name='student_work'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/download_student_submission/<str:student>', views.download_student_activity_submission, name='instructor_download_activity_submission'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/student_work/<str:fk>', views.save_activity_grades, name='save_activity_grades'),
    path('instructor/edit_profile/', views.edit_profile,name="instructor_edit_profile"),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/student_work/private_comments/<int:student>', views.private_comments, name='instructor_private_comments'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/student_work/private_comments/<int:student>/add', views.add_private_comment_instructor, name='instructor_private_comments_add'),
    path('instructor/view_courses/<str:id>/assignments/comments/<int:pk>/student_work/private_comments/<int:student>/delete/<int:comment_id>', views.delete_private_comment_instructor, name='instructor_private_comments_delete'),
    path('instructor/calendar', views.calendar, name='calendar'),

      
    
]
   
