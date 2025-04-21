from django.urls import path
from . import views

app_name = 'event_news'

urlpatterns = [
    path('', views.views_news, name='views_news'),
    path('add/', views.add_content, name='add_content'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
]
