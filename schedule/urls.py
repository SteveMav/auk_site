from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
     path('', views.course_list, name='course_list'),
     path('create_course/', views.create_course_with_schedule, name='create_course_with_schedule'),
     # path('create_schedule/', views.create_schedule, name='create_schedule'),
]