from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model


def send_news_email(news, request):
    User = get_user_model()
    users = User.objects.filter(is_active=True).exclude(email='')
    subject = f"Nouvelle actualité : {news.title}"
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
