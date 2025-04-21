from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('deconnect/', views.deconnect, name='deconnect'),
    path('enter-code/', views.enter_confirmation_code, name='enter_code'),
    path('resend-code/', views.resend_confirmation_code, name='resend_code'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]
