from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Course

def send_course_added_email(course, request, schedule_info=None):
    User = get_user_model()
    # Notify all users of the faculty (students, CPs, etc.) who have an email
    users = User.objects.filter(is_active=True, userprofile__faculty=course.faculty).exclude(email='')
    subject = f"Nouveau cours ajouté : {course.name}"
    course_url = request.build_absolute_uri(f"/schedule/course/{course.id}/")
    for user in users:
        html_content = render_to_string('schedule/course_added_email.html', {
            'user': user,
            'course': course,
            'course_url': course_url,
            'schedule_info': schedule_info,
        })
        msg = EmailMultiAlternatives(
            subject,
            f"Bonjour {user.first_name or user.username}, un nouveau cours a été ajouté : {course.name}",
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)

def send_course_updated_email(course, request, schedule=None):
    User = get_user_model()
    users = User.objects.filter(is_active=True, userprofile__faculty=course.faculty).exclude(email='')
    subject = f"Modification d'un cours : {course.name}"
    course_url = request.build_absolute_uri(f"/schedule/course/{course.id}/")
    
    # Préparer les informations d'horaire
    schedule_info = ""
    if schedule:
        # Pas besoin de mapping car day_of_week est déjà le nom du jour
        day_name = schedule.day_of_week
        schedule_info = f"{day_name} de {schedule.start_time.strftime('%H:%M')} à {schedule.end_time.strftime('%H:%M')}"
    
    for user in users:
        html_content = render_to_string('schedule/course_updated_email.html', {
            'user': user,
            'course': course,
            'course_url': course_url,
            'schedule': schedule,
            'schedule_info': schedule_info,
        })
        msg = EmailMultiAlternatives(
            subject,
            f"Bonjour {user.first_name or user.username}, un cours a été modifié : {course.name}",
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
