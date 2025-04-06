from django.urls import path
from . import views

app_name = 'event_news'

urlpatterns = [
    path('add/', views.add_content, name='add_content'),
]
