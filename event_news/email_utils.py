from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model


def send_news_email(news, request):
    User = get_user_model()
    
    # Si la news est publique, envoyer à tous les utilisateurs
    if news.is_public:
        users = User.objects.filter(is_active=True).exclude(email='')
    else:
        # Sinon, filtrer les utilisateurs par faculté
        # Récupérer les utilisateurs qui ont un profil avec une faculté ciblée
        from accounts.models import UserProfile
        target_faculty_ids = news.target_faculties.values_list('id', flat=True)
        user_profiles = UserProfile.objects.filter(faculty__id__in=target_faculty_ids)
        user_ids = user_profiles.values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids, is_active=True).exclude(email='')
    
    subject = f"Nouvelle actualité : {news.title}"
    
    # Journaliser le nombre d'emails envoyés pour debug
    print(f"Envoi de {users.count()} emails pour la news '{news.title}'")
    
    for user in users:
        html_content = render_to_string('event_news/news_email.html', {
            'user': user,
            'news': news,
            'news_url': request.build_absolute_uri(news.get_absolute_url()),
        })
        msg = EmailMultiAlternatives(
            subject,
            f"Bonjour {user.first_name or user.username}, une nouvelle actualité est publiée : {news.title}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)

def send_event_email(event, request):
    User = get_user_model()
    users = User.objects.filter(is_active=True).exclude(email='')
    subject = f"Nouvel événement : {event.title}"
    for user in users:
        html_content = render_to_string('event_news/event_email.html', {
            'user': user,
            'event': event,
            'event_url': request.build_absolute_uri(event.get_absolute_url()),
        })
        msg = EmailMultiAlternatives(
            subject,
            f"Bonjour {user.first_name or user.username}, un nouvel événement est publié : {event.title}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
