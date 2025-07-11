from django.urls import path
from . import views

app_name = 'librairy'

urlpatterns = [
    path('', views.library_home, name='library_home'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('upload/', views.upload_content, name='upload_content'),
    path('upload/article/', views.upload_article, name='upload_article'),
    path('upload/book/', views.upload_book, name='upload_book'),
]
