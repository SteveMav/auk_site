from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
     path('', views.course_list, name='course_list'),
     path('course/<int:course_id>/files/partial_list/', views.ajax_course_file_list_partial, name='ajax_course_file_list_partial'),
     path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
     path('schedule/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
     path('create_course/', views.create_course, name='create_course'),
     path('edit_schedule/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
     path('works/', views.work_list, name='work_list'),
     path('works/create/', views.create_work, name='create_work'),
     path('course/', views.all_courses_view, name='all_courses'),
     path('course/<int:course_id>/files/', views.course_files_view, name='course_files_view'),
     path('course/<int:course_id>/files/ajax_upload/', views.ajax_upload_course_file, name='ajax_upload_course_file'),
     path('course/file/<int:file_id>/ajax_delete/', views.ajax_delete_course_file, name='ajax_delete_course_file'),
     path('course/file/<int:file_id>/delete/', views.delete_course_file, name='delete_course_file'),
     path('exams/create/', views.create_exam, name='create_exam'),
     path('exams/', views.exam_list, name='exam_list'),
]