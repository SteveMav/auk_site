from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordChangeForm

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.deconnect, name='logout'),
    path('enter-code/', views.enter_confirmation_code, name='enter_code'),
    path('resend-code/', views.resend_confirmation_code, name='resend_code'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/edit-profile/',
        form_class=CustomPasswordChangeForm
    ), name='password_change'),
]
