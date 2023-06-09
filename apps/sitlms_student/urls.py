from django.urls import path
from django.contrib import admin
from apps.sitlms_student import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('student_profile', views.student_profile,name="student_profile"),
    path('student_profile/<int:id>', views.read_notif, name="read_notif"),
    path('student_profile/course_details/', views.student_course_details,name="course_details"),
    path('student_profile/report_issues', views.report_issues,name="report_issues"),
    path('student_profile/edit_profile/', views.student_edit_profile,name="edit_profile"),
    path('student_profile/view_courses/<str:id>', views.student_view_course, name='view_courses'),
    path('student_profile/view_courses/<str:id>/assignment/<int:pk>', views.student_view_assignment_details, name='student_view_assignment_details'),
    path('student_profile/view_courses/<str:id>/assignment/<int:pk>/add_private_comment', views.add_private_comment_student, name='student_add_private_comment'),
    path('student_profile/view_courses/<str:id>/assignment/<int:pk>/delete_private_comment/<int:comment_id>', views.delete_private_comment_student, name='student_delete_private_comment'),
    path('student_profile/view_courses/<str:id>/assignments/<int:pk>/download-attachment', views.download_activity_attachment, name='student_download_activity_attachment'),
    path('student-no-access',views.custom_403_2,name="student-no-access"),
    path('student_profile/view_courses/<str:id>/assignment/<int:pk>/upload_activity_submission',views.upload_activity_submission,name="upload_activity_submission"),
    path('student_profile/view_courses/<str:id>/assignments/<int:pk>/download_activity_submission', views.download_activity_submission, name='download_activity_submission'),
    path('student_profile/view_courses/<str:id>/assignment/<int:pk>/edit/<int:fk>',views.edit_student_comment,name='edit_student_comment'),
    path('student_profile/view_courses/<str:id>/assignment/<int:pk>/delete/<int:fk>',views.delete_student_comment,name='delete_student_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)