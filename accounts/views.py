from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .forms import RegistrationForm, LoginForm, ConfirmationCodeForm, UserProfileForm
from .models import PendingRegistration, UserProfile

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Supprimer toute inscription en attente existante pour cet email
            PendingRegistration.objects.filter(email=email).delete()
            
            # Créer une nouvelle inscription en attente
            pending = PendingRegistration(
                email=email,
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                faculty=form.cleaned_data['faculty']
            )
            pending.save()

            # Préparer et envoyer l'email
            subject = 'Code de confirmation - Inscription'
            message = render_to_string('accounts/confirmation_email.html', {
                'last_name': pending.last_name,
                'confirmation_code': pending.confirmation_code,
            })

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                    html_message=message
                )
                messages.success(
                    request,
                    'Un code de confirmation a été envoyé à votre adresse email.'
                )
                # Rediriger vers la page de saisie du code
                return redirect('accounts:enter_code')
            except Exception as e:
                pending.delete()
                messages.error(
                    request,
                    'Erreur lors de l\'envoi du code de confirmation. Veuillez réessayer.'
                )
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def enter_confirmation_code(request):
    if request.method == 'POST':
        form = ConfirmationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                # Chercher l'inscription en attente avec ce code
                pending = PendingRegistration.objects.get(confirmation_code=code)
                
                # Vérifier si le code n'a pas expiré
                if pending.is_expired():
                    pending.delete()
                    messages.error(request, 'Le code de confirmation a expiré. Veuillez vous réinscrire.')
                    return redirect('accounts:register')
                
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=pending.email,
                    email=pending.email,
                    password=pending.password,
                    first_name=pending.first_name,
                    last_name=pending.last_name
                )
                
                # Créer le profil utilisateur
                UserProfile.objects.create(
                    user=user,
                    faculty=pending.faculty
                )
                
                # Supprimer l'inscription en attente
                pending.delete()
                
                # Connecter l'utilisateur
                login(request, user)
                messages.success(request, 'Votre compte a été activé avec succès!')
                return redirect('main:index')
                
            except PendingRegistration.DoesNotExist:
                messages.error(request, 'Code de confirmation invalide.')
    else:
        form = ConfirmationCodeForm()
    
    return render(request, 'accounts/enter_confirmation_code.html', {'form': form})

def resend_confirmation_code(request):
    # Récupérer la dernière inscription en attente pour l'utilisateur
    try:
        pending = PendingRegistration.objects.filter(email=request.session.get('registration_email')).latest('created_at')
        
        # Générer un nouveau code
        pending.confirmation_code = pending.generate_confirmation_code()
        pending.created_at = timezone.now()
        pending.save()
        
        # Renvoyer l'email
        subject = 'Nouveau code de confirmation - Inscription'
        message = render_to_string('accounts/confirmation_email.html', {
            'email': pending.email,
            'confirmation_code': pending.confirmation_code,
        })
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [pending.email],
            fail_silently=False,
            html_message=message
        )
        
        messages.success(request, 'Un nouveau code de confirmation a été envoyé.')
    except PendingRegistration.DoesNotExist:
        messages.error(request, 'Aucune inscription en attente trouvée. Veuillez vous réinscrire.')
        return redirect('accounts:register')
    
    return redirect('accounts:enter_code')



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

    



def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('accounts:edit_profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'accounts/edit_profile.html', {'form': form, 'user_profile': user_profile})

def deconnect(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('main:index')
