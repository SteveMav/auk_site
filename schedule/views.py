from django.contrib.auth.forms import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from .models import Course, CourseSchedule, Work, CPProfile, CourseFile, Exam
from .forms import CourseForm, CourseScheduleForm, WorkForm, CourseFileForm, CourseFileMultipleForm, ExamForm
from django.template.loader import render_to_string
import json
from accounts.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from datetime import timedelta

@login_required
@permission_required('schedule.add_coursefile')
def upload_course_files(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_superuser:
        try:
            cp_profile = CPProfile.objects.get(user=request.user)
            if course.faculty != cp_profile.faculty:
                return HttpResponseForbidden("Vous ne pouvez ajouter des fichiers que pour votre propre faculté.")
        except CPProfile.DoesNotExist:
            return HttpResponseForbidden("Accès non autorisé.")
    if request.method == 'POST':
        form = CourseFileMultipleForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        description = request.POST.get('description', '')
        if form.is_valid():
            for file in files:
                CourseFile.objects.create(course=course, file=file, description=description)
            messages.success(request, 'Fichiers ajoutés avec succès.')
            return redirect('schedule:course_files_view', course_id=course.id)
    else:
        form = CourseFileMultipleForm()
    return render(request, 'schedule/upload_course_files.html', {'form': form, 'course': course})

@login_required
def delete_course_file(request, file_id):
    file = get_object_or_404(CourseFile, id=file_id)
    course = file.course
    if not request.user.is_superuser:
        try:
            cp_profile = CPProfile.objects.get(user=request.user)
            if course.faculty != cp_profile.faculty:
                return HttpResponseForbidden("Vous ne pouvez supprimer que les fichiers de votre propre faculté.")
        except CPProfile.DoesNotExist:
            return HttpResponseForbidden("Accès non autorisé.")
    if request.method == 'POST':
        file.delete()
        messages.success(request, 'Fichier supprimé avec succès.')
        return redirect('schedule:course_files_view', course_id=course.id)
    return render(request, 'schedule/delete_course_file.html', {'file': file, 'course': course})

@login_required
def course_files_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    files = course.files.all()
    return render(request, 'schedule/course_files_view.html', {'course': course, 'files': files})

from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Seuls les superusers ou CP de la même faculté peuvent supprimer
    if not request.user.is_superuser:
        try:
            cp_profile = CPProfile.objects.get(user=request.user)
            if course.faculty != cp_profile.faculty:
                return HttpResponseForbidden("Vous ne pouvez supprimer que les cours de votre propre faculté.")
        except CPProfile.DoesNotExist:
            return HttpResponseForbidden("Accès non autorisé.")
    course.delete()
    messages.success(request, f'Le cours "{course.name}" a été supprimé avec succès.')
    return redirect('schedule:course_list')

@login_required
@permission_required('schedule.add_course')
def create_course(request):
    days = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche')
    cp_profile = None

    if request.user.is_superuser:
        cp_profile = None
    else:
        cp_profile = CPProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)

            # Empêcher la création pour une autre faculté
            if not request.user.is_superuser and course.faculty != cp_profile.faculty:
                return HttpResponseForbidden("Vous ne pouvez créer un cours que pour votre propre faculté.")

            course.save()

            # Enregistrement du PDF s'il existe
            pdf_file = form.cleaned_data.get('pdf_file')
            if pdf_file:
                from .models import CourseFile
                CourseFile.objects.create(course=course, file=pdf_file, description='PDF ajouté à la création du cours')

            # Création des horaires avec validation
            schedule_data = json.loads(request.POST.get('schedules', '{}'))
            schedule_creation_failed = False

            for day, blocks in schedule_data.items():
                schedules_to_create = []
                if 'morning' in blocks:
                    schedules_to_create.append({
                        'day_of_week': day,
                        'start_time': '08:00',
                        'end_time': '12:00'
                    })
                if 'afternoon' in blocks:
                    schedules_to_create.append({
                        'day_of_week': day,
                        'start_time': '13:00',
                        'end_time': '16:00'
                    })

                for schedule_data in schedules_to_create:
                    schedule_form = CourseScheduleForm({
                        'course': course.id,
                        **schedule_data
                    })
                    
                    if schedule_form.is_valid():
                        schedule_form.save()
                    else:
                        schedule_creation_failed = True
                        error_messages = [f"{error}" for error in schedule_form.errors.values()]
                        messages.error(request, f"Erreur lors de la création de l'horaire pour {day}: {' '.join(error_messages)}")

            if schedule_creation_failed:
                # Si la création d'horaire a échoué, supprimer le cours
                course.delete()
                return render(request, 'schedule/create_course.html', {'form': form, 'days': days})

            # Envoi de l'email de notification après création du cours
            from .email_utils import send_course_added_email
            schedules = course.courseschedule_set.all()
            schedule_info = [f"{s.get_day_of_week_display()}: {s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}" for s in schedules]
            send_course_added_email(course, request, schedule_info=schedule_info)

            return redirect('schedule:course_list')
    else:
        form = CourseForm()

        # Restreindre la faculté dans le formulaire (juste celle du CP)
        if cp_profile:
            form.fields['faculty'].queryset = form.fields['faculty'].queryset.filter(id=cp_profile.faculty.id)

    return render(request, 'schedule/create_course.html', {'form': form, 'days': days})



@login_required
def course_list(request):
    # Dictionnaire de traduction des jours
    day_translation = {
        'Lundi': 'Lundi',
        'Mardi': 'Mardi',
        'Mercredi': 'Mercredi',
        'Jeudi': 'Jeudi',
        'Vendredi': 'Vendredi',
        'Samedi': 'Samedi',
        'Dimanche': 'Dimanche',
    }
    
    days_of_week = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    # Get courses based on user role
    if request.user.is_superuser:
        courses = Course.objects.prefetch_related('courseschedule_set')
    elif not request.user.is_staff:
        courses = Course.objects.filter(faculty__userprofile__user=request.user).prefetch_related('courseschedule_set')
    else:
        cp_profile = CPProfile.objects.get(user=request.user)
        courses = Course.objects.filter(faculty=cp_profile.faculty).prefetch_related('courseschedule_set')
    
    # Organize courses by day
    courses_by_day = {day: [] for day in days_of_week}
    
    for course in courses:
        for schedule in course.courseschedule_set.all():
            # Traduire le jour de l'anglais vers le français
            french_day = day_translation.get(schedule.day_of_week)
            if french_day:
                courses_by_day[french_day].append({
                    'course': course,
                    'schedule': schedule
                })
    
    context = {
        'days_of_week': days_of_week,
        'courses_by_day': courses_by_day
    }
    
    return render(request, 'schedule/course_list.html', context)



@login_required
@permission_required('schedule.change_courseschedule')
def edit_schedule(request, schedule_id):
    schedule = CourseSchedule.objects.get(id=schedule_id)
    course = schedule.course

    # Vérifier que l'utilisateur a le droit de modifier cet horaire
    if not request.user.is_superuser:
        try:
            cp_profile = CPProfile.objects.get(user=request.user)
            if course.faculty != cp_profile.faculty:
                return HttpResponseForbidden("Vous ne pouvez modifier que les horaires de votre faculté.")
        except CPProfile.DoesNotExist:
            return HttpResponseForbidden("Accès non autorisé.")

    if request.method == 'POST':
        form = CourseScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Horaire modifié avec succès.')
            from .email_utils import send_course_updated_email
            send_course_updated_email(course, request)
            return redirect('schedule:course_list')
    else:
        form = CourseScheduleForm(instance=schedule)

    return render(request, 'schedule/edit_schedule.html', {
        'form': form,
        'schedule': schedule,
        'course': course
    })

from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(CourseSchedule, id=schedule_id)
    course = schedule.course
    # Permissions identiques à edit_schedule
    if not request.user.is_superuser:
        try:
            cp_profile = CPProfile.objects.get(user=request.user)
            if course.faculty != cp_profile.faculty:
                return HttpResponseForbidden("Vous ne pouvez supprimer que les horaires de votre faculté.")
        except CPProfile.DoesNotExist:
            return HttpResponseForbidden("Accès non autorisé.")
    schedule.delete()
    messages.success(request, f"L'horaire du cours '{course.name}' ({schedule.start_time} - {schedule.end_time}) a été supprimé avec succès.")
    return redirect('schedule:course_list')

@login_required
def create_work(request):
    # Vérifier si l'utilisateur est un CP ou un superuser
    if not hasattr(request.user, 'cpprofile') and not request.user.is_superuser:
        return HttpResponseForbidden("Seuls les CP et les superusers peuvent créer des TP.")

    if request.method == 'POST':
        form = WorkForm(request.POST, request.FILES, faculty=request.user.cpprofile.faculty if hasattr(request.user, 'cpprofile') else None)
        if form.is_valid():
            work = form.save()
            # Envoi d'un mail à tous les étudiants de la faculté du TP
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.conf import settings
            from accounts.models import UserProfile
            # Récupérer tous les étudiants de la faculté du cours du TP
            faculty = work.course.faculty
            students = UserProfile.objects.filter(faculty=faculty, user__is_active=True, user__email__isnull=False)
            recipient_list = [s.user.email for s in students if s.user.email]
            tp_url = request.build_absolute_uri('/schedule/works/')
            subject = f"Nouveau TP pour le cours {work.course.name}"
            html_message = render_to_string('emails/new_work_notification.html', {
                'work': work,
                'tp_url': tp_url,
            })
            send_mail(
                subject,
                '',  # plain message (vide, car on utilise html)
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                html_message=html_message,
                fail_silently=True,
            )
            messages.success(request, 'Le TP a été créé avec succès. Les étudiants ont été notifiés par email.')
            return redirect('schedule:work_list')
    else:
        form = WorkForm(faculty=request.user.cpprofile.faculty if hasattr(request.user, 'cpprofile') else None)
    
    return render(request, 'schedule/create_work.html', {'form': form})



@login_required
def work_list(request):
    now = timezone.now() + timedelta(hours=1)
    user = request.user
    if user.is_superuser:
        works = Work.objects.all().order_by('-due_date')
    elif hasattr(user, 'cpprofile'):
        works = Work.objects.filter(course__faculty=user.cpprofile.faculty).order_by('-due_date')
    elif hasattr(user, 'student'):
        works = Work.objects.filter(course__faculty=user.student.faculty).order_by('-due_date')
    else:
        works = Work.objects.none()
    now = timezone.now() + timedelta(hours=1)
    return render(request, 'schedule/work_list.html', {'works': works, 'now': now})

def all_courses_view(request):
    user = request.user
    if user.is_superuser:
        courses = Course.objects.all().prefetch_related('files', 'faculty')
    elif hasattr(user, 'cpprofile'):
        courses = Course.objects.filter(faculty=user.cpprofile.faculty).prefetch_related('files', 'faculty')
    else:
        try:
            faculty = UserProfile.objects.get(user=user).faculty
            courses = Course.objects.filter(faculty=faculty).prefetch_related('files', 'faculty')
        except (UserProfile.DoesNotExist, ObjectDoesNotExist):
            courses = Course.objects.none()
    return render(request, 'schedule/all_courses.html', {'courses': courses})


@login_required
def create_exam(request):
    # Seuls les CP et les admins peuvent créer
    if not request.user.is_superuser and not hasattr(request.user, 'cpprofile'):
        return HttpResponseForbidden("Seuls les CP et les administrateurs peuvent ajouter un examen.")

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, "Examen ajouté avec succès.")
            return redirect('schedule:exam_list')
    else:
        form = ExamForm()
    return render(request, 'schedule/exam_form.html', {'form': form})


@login_required
def exam_list(request):
    # CP : examens de sa faculté, étudiant : idem, admin : tout
    if hasattr(request.user, 'cpprofile'):
        exams = Exam.objects.filter(course__faculty=request.user.cpprofile.faculty, date__gte=timezone.now()).order_by('date')
    elif hasattr(request.user, 'student'):
        exams = Exam.objects.filter(course__faculty=request.user.student.faculty, date__gte=timezone.now()).order_by('date')
    else:
        exams = Exam.objects.filter(date__gte=timezone.now()).order_by('date')
    return render(request, 'schedule/exam_list.html', {'exams': exams})


@login_required
@permission_required('schedule.add_coursefile')
def ajax_upload_course_file(request, course_id):
    if request.method == 'POST' and request.FILES.get('file'):
        course = get_object_or_404(Course, id=course_id)
        file = request.FILES['file']
        description = request.POST.get('description', '')
        CourseFile.objects.create(course=course, file=file, description=description)
        files = course.files.all()
        file_list_html = render_to_string('schedule/partials/course_file_list.html', {'course': course, 'files': files, 'user': request.user, 'perms': request.user.get_all_permissions()})
        return JsonResponse({'file_list_html': file_list_html})
    return JsonResponse({'error': 'Erreur lors de l\'upload.'}, status=400)


@login_required
@permission_required('schedule.delete_coursefile')
def ajax_delete_course_file(request, file_id):
    if request.method == 'POST':
        file = get_object_or_404(CourseFile, id=file_id)
        course = file.course
        file.delete()
        files = course.files.all()
        file_list_html = render_to_string('schedule/partials/course_file_list.html', {'course': course, 'files': files, 'user': request.user, 'perms': request.user.get_all_permissions()})
        return JsonResponse({'file_list_html': file_list_html})
    return JsonResponse({'error': 'Erreur lors de la suppression.'}, status=400)

