from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.conf import settings
from .models import Article, Books
from .forms import ArticleForm, BookForm
from django.template.loader import render_to_string
from .utils import send_content_notification
from django.contrib.sites.shortcuts import get_current_site


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


def book_detail(request, book_id):
    """
    Vue pour afficher le détail d'un livre
    """
    book = get_object_or_404(Books, id=book_id)
    
    # Récupérer les 3 derniers livres (pour la section "Livres similaires")
    related_books = Books.objects.exclude(id=book_id).order_by('-date_published')[:3]
    
    context = {
        'book': book,
        'related_books': related_books,
        'title': f"{book.title} - Bibliothèque AUK"
    }
    
    return render(request, 'librairy/book_detail.html', context)


@permission_required('librairy.add_article')
@login_required
def upload_content(request):
    """
    Vue pour l'upload des articles et livres
    """
    article_form = ArticleForm()
    book_form = BookForm()
    
    context = {
        'article_form': article_form,
        'book_form': book_form,
        'title': 'Ajouter du contenu - Bibliothèque AUK'
    }
    
    return render(request, 'librairy/upload_content.html', context)

@require_http_methods(["POST"])
@login_required
def upload_article(request: HttpRequest):
    """
    Vue pour l'upload asynchrone d'un article
    """
    form = ArticleForm(request.POST, request.FILES)
    if form.is_valid():
        article = form.save(commit=False)
        article.author = request.user
        article.save()
        
        # Envoyer une notification par email
        current_site = get_current_site(request)
        absolute_url = f"https://{current_site.domain}{article.get_absolute_url()}"
        
        # Préparer l'image pour l'email
        image_file = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            # Remettre le curseur au début du fichier
            image_file.seek(0)
        
        send_content_notification(
            content_type='article',
            title=article.title,
            author=article.author,
            created_date=article.created_date,
            absolute_url=absolute_url,
            description=article.content[:200],  # On envoie les 200 premiers caractères
            image_file=image_file
        )
        
        # Préparer les données pour la réponse JSON
        article_data = model_to_dict(article, fields=['id', 'title', 'created_date'])
        article_data['created_date'] = article.created_date.strftime('%d %B %Y')
        article_data['author_name'] = article.author.get_full_name() or article.author.username
        
        return JsonResponse({
            'success': True,
            'message': 'Article ajouté avec succès! Une notification a été envoyée à tous les utilisateurs.',
            'article': article_data,
            'html': render_to_string('librairy/includes/article_card.html', {
                'article': article
            })
        })
    
    # Si le formulaire n'est pas valide, renvoyer les erreurs
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)

@require_http_methods(["POST"])
@login_required
def upload_book(request: HttpRequest):
    """
    Vue pour l'upload asynchrone d'un livre
    """
    form = BookForm(request.POST, request.FILES)
    if form.is_valid():
        book = form.save(commit=False)
        book.publisher = request.user
        book.save()
        
        # Envoyer une notification par email
        current_site = get_current_site(request)
        absolute_url = f"https://{current_site.domain}{book.get_absolute_url()}"
        
        # Préparer l'image pour l'email
        image_file = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            # Remettre le curseur au début du fichier
            image_file.seek(0)
        
        send_content_notification(
            content_type='livre',
            title=book.title,
            author=book.publisher,  # L'utilisateur qui a publié le livre
            created_date=book.date_published,
            absolute_url=absolute_url,
            description=book.description,
            image_file=image_file
        )
        
        # Préparer les données pour la réponse JSON
        book_data = model_to_dict(book, fields=['id', 'title', 'author', 'date_published'])
        book_data['date_published'] = book.date_published.strftime('%d %B %Y')
        book_data['publisher_name'] = book.publisher.get_full_name() or book.publisher.username
        
        return JsonResponse({
            'success': True,
            'message': 'Livre ajouté avec succès! Une notification a été envoyée à tous les utilisateurs.',
            'book': book_data,
            'html': render_to_string('librairy/includes/book_card.html', {
                'book': book
            })
        })
    
    # Si le formulaire n'est pas valide, renvoyer les erreurs
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)