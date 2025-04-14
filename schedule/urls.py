from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
     path('', views.course_list, name='course_list'),
     path('create_course/', views.create_course, name='create_course'),
     path('edit_schedule/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
]