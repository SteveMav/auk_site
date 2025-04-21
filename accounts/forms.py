from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from schedule.models import Faculty
from .models import UserProfile

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-lg'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['numero_matricule', 'photo', 'faculty']
        widgets = {
            'numero_matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
        }

class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nom'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Prenom'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Email'
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Mot de passe'
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmer le mot de passe'
    )
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Faculte'
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        email = cleaned_data.get('email')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')

        if email:
            if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
                raise forms.ValidationError('Un utilisateur avec cet email existe déjà.')

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur ou email",
        widget=forms.TextInput(attrs={'class': 'form-control my-3', 'id': 'usernameInput'}),
        required=True
    )
    password = forms.CharField(
        max_length=128,
        required=True,
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control my-3', 'id': 'passwordInput'})
    )

class ConfirmationCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        label='Code de confirmation',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Entrez le code à 6 chiffres',
            'pattern': '[0-9]{6}',
            'title': 'Le code doit contenir 6 chiffres',
            'autocomplete': 'off',
            'aria-describedby': 'codeHelpBlock'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].help_text = '<small id="codeHelpBlock" class="form-text text-muted">Entrez le code à 6 chiffres envoyé à votre adresse e-mail.</small>'

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError('Le code doit contenir uniquement des chiffres.')
        return code
