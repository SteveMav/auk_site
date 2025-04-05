from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from schedule.models import Faculty
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Faculte'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'first_name': 'Nom',
            'last_name': 'Prenom',
            'email': 'Email',
            'password1': 'Mot de passe',
            'password2': 'Confirmer le mot de passe',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Using email as username
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                faculty=self.cleaned_data['faculty']
            )
        return user


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=15, 
        required=True, 
        label='Email', 
        widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'usernameInput'}), 
        help_text=''
    )
    password = forms.CharField(
        max_length=15, 
        required=True, 
        label='Mot de passe', 
        widget=forms.PasswordInput(attrs={'class': 'form-control my-3', 'id': 'passwordInput'}), 
        help_text=''
    )
    
    # Custom initialization of the login form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class': 'form-control my-3', 'id': 'passwordInput'})
        self.fields['password'].help_text = ''
        self.fields['password'].label = 'Mot de passe'
