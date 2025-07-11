from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Article, Books
from django.contrib.auth.decorators import login_required


@login_required
def library_home(request):
    """
    Vue principale de la bibliothèque affichant les articles et les livres
    """
    # Récupérer les 6 derniers articles
    articles = Article.objects.all().order_by('-created_date')[:6]
    
    # Récupérer les 6 derniers livres
    books = Books.objects.all().order_by('-date_published')[:6]
    
    context = {
        'articles': articles,
        'books': books,
        'title': 'Bibliothèque AUK'
    }
    
    return render(request, 'librairy/base_librairy.html', context)

@login_required
def article_detail(request, article_id):
    """
    Vue pour afficher le détail d'un article
    """
    article = get_object_or_404(Article, id=article_id)
    
    # Récupérer les 3 derniers articles (pour la section "Articles similaires")
    related_articles = Article.objects.exclude(id=article_id).order_by('-created_date')[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'title': f"{article.title} - Bibliothèque AUK"
    }
    
    return render(request, 'librairy/article_detail.html', context)