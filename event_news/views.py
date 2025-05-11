from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import NewsForm, EventForm
from .models import News, Event
from .email_utils import send_news_email, send_event_email
from django.shortcuts import get_object_or_404
from django.urls import reverse

@login_required
def add_content(request):
    news_form = NewsForm()
    event_form = EventForm()

    if request.method == 'POST':
        if 'submit_news' in request.POST:
            news_form = NewsForm(request.POST, request.FILES)
            if news_form.is_valid():
                news = news_form.save(commit=False)
                news.created_by = request.user
                news.save()
                
                # Sauvegarder les relations many-to-many après avoir sauvegardé l'objet
                news_form.save_m2m()
                
                # Envoyer l'email aux utilisateurs concernés
                messages.success(request, 'News ajoutée avec succès!')
                send_news_email(news, request)
                return redirect('event_news:add_content')
            else:
                messages.error(request, 'Erreur dans le formulaire de news.')
        
        elif 'submit_event' in request.POST:
            event_form = EventForm(request.POST)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                event.created_by = request.user
                event.save()
                # send_event_email(event, request)
                messages.success(request, 'Événement créé avec succès!')
                return redirect('event_news:add_content')
            else:
                messages.error(request, 'Erreur dans le formulaire d\'événement.')

    context = {
        'news_form': news_form,
        'event_form': event_form
    }
    return render(request, 'event_news/add_content.html', context)

@login_required
def views_news(request):
    # Récupérer la faculté de l'utilisateur connecté
    from accounts.models import UserProfile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_faculty = user_profile.faculty
    except UserProfile.DoesNotExist:
        user_faculty = None
    
    # Créer la requête de base pour les news
    base_query = News.objects.all()
    
    # Toujours inclure les news publiques, quel que soit l'utilisateur
    conditions = models.Q(is_public=True)
    
    # Si l'utilisateur a une faculté, ajouter les news ciblées pour cette faculté
    if user_faculty:
        conditions |= models.Q(target_faculties=user_faculty)
    
    # Appliquer les filtres et ordonner par date de création (plus récentes d'abord)
    news = base_query.filter(conditions).distinct().order_by('-created_at')
    
    # Journaliser le nombre de news trouvées pour debug
    print(f"Nombre de news trouvées pour l'utilisateur {request.user}: {news.count()}")
    if user_faculty:
        print(f"Faculté de l'utilisateur: {user_faculty.name}")
    
    return render(request, 'event_news/news.html', {'news': news})

@login_required
def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'event_news/news_detail.html', {'news': news})

