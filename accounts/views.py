from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegistrationForm, LoginForm

def register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('main:index')
            else:
                messages.error(request, 'Error logging in after account creation.')
        else:
            # Handle form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, 'Error in field {}: {}'.format(field, error))

    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('main:index')
            else:
                messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html', {'form': form})

def deconnect(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('main:index')
