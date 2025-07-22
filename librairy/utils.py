from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_content_notification(content_type, title, author, created_date, absolute_url, image_url=None, description=None, image_file=None):
    """
    Envoie une notification par email pour un nouveau contenu publié
    
    Args:
        content_type (str): Type de contenu ('article' ou 'livre')
        title (str): Titre du contenu
        author: L'auteur du contenu (instance User)
        created_date: Date de création
        absolute_url (str): URL absolue vers le contenu
        image_url (str, optional): URL de l'image du contenu (déprécié, utiliser image_file)
        description (str, optional): Description du contenu
        image_file (InMemoryUploadedFile, optional): Fichier image à intégrer
    """
    # Récupérer tous les utilisateurs actifs qui veulent recevoir des notifications
    users = get_user_model().objects.filter(is_active=True, email__isnull=False).exclude(email='')
    
    # Sujet de l'email
    subject = f'Nouveau {content_type} publié : {title}'
    
    # Préparer l'image une seule fois si elle existe
    image_data = None
    if image_file and hasattr(image_file, 'file'):
        # Sauvegarder la position actuelle du fichier
        current_position = image_file.tell()
        image_file.seek(0)
        image_data = image_file.read()
        # Remettre le curseur à sa position d'origine
        image_file.seek(current_position)
    
    # Compter les échecs d'envoi
    success_count = 0
    failure_count = 0
    
    # Envoyer un email individuel à chaque utilisateur
    for user in users:
        # Préparer le contexte pour le template d'email
        context = {
            'content_type': content_type,
            'title': title,
            'author_name': author.get_full_name() or author.username,
            'created_date': created_date,
            'absolute_url': absolute_url,
            'has_image': image_data is not None,
            'description': description,
            'user': user,  # Ajout de l'utilisateur au contexte pour personnalisation
        }
        
        # Rendre le template HTML
        html_message = render_to_string('librairy/emails/new_content_notification.html', context)
        
        # Créer la version texte du message
        plain_message = strip_tags(html_message)
        
        # Créer le message email
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],  # Un seul destinataire par email
            )
            email.attach_alternative(html_message, "text/html")
            
            # Si une image est fournie, l'intégrer dans l'email
            if image_data:
                # Créer un nouvel objet MIMEImage pour chaque email
                image = MIMEImage(image_data)
                image.add_header('Content-ID', '<content_image>')
                image.add_header('Content-Disposition', 'inline', 
                               filename=f"{slugify(title)[:20]}.{image_file.name.split('.')[-1] if hasattr(image_file, 'name') else 'jpg'}")
                
                # Attacher l'image au message
                email.attach(image)
                
                # Mettre à jour le contenu HTML pour utiliser l'image intégrée
                html_message = html_message.replace(
                    'src="cid:content_image"',
                    'src="cid:content_image" style="max-width: 100%; height: auto; border-radius: 8px; margin: 15px 0; display: block;"'
                )
                email.attach_alternative(html_message, "text/html")
            
            # Envoyer l'email
            email.send(fail_silently=False)
            success_count += 1
            
        except Exception as e:
            print(f"Erreur lors de l'envoi à {user.email}: {str(e)}")
            failure_count += 1
    
    # Retourner un résumé de l'opération
    return {
        'total_recipients': len(users),
        'success_count': success_count,
        'failure_count': failure_count
    }
