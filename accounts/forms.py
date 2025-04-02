from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from schedule.models import Faculty

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','faculty', 'email', 'password1', 'password2',]