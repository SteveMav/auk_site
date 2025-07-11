from django.urls import path
from . import views

app_name = 'librairy'

urlpatterns = [
    path('', views.library_home, name='library_home'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
]
