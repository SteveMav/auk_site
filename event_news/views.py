from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import NewsForm, EventForm
from .models import News, Event

# Create your views here.

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
                messages.success(request, 'News ajoutée avec succès!')
                return redirect('event_news:add_content')
            else:
                messages.error(request, 'Erreur dans le formulaire de news.')
        
        elif 'submit_event' in request.POST:
            event_form = EventForm(request.POST)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                event.created_by = request.user
                event.save()
                messages.success(request, 'Événement créé avec succès!')
                return redirect('event_news:add_content')
            else:
                messages.error(request, 'Erreur dans le formulaire d\'événement.')

    context = {
        'news_form': news_form,
        'event_form': event_form
    }
    return render(request, 'event_news/add_content.html', context)


def views_news(request):
    news = News.objects.all()
    return render(request, 'event_news/news.html', {'news': news})
