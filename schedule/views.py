from django.contrib.auth.forms import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from .models import Course, CourseSchedule, Work, CPProfile
from .forms import CourseForm, CourseScheduleForm, WorkForm
import json



@login_required
@permission_required('schedule.add_course')
def create_course(request):
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    cp_profile = None

    if request.user.is_superuser:
        cp_profile = None
    else:
        cp_profile = CPProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)

            # Empêcher la création pour une autre faculté
            if not request.user.is_superuser and course.faculty != cp_profile.faculty:
                return HttpResponseForbidden("Vous ne pouvez créer un cours que pour votre propre faculté.")

            course.save()

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
                        'start_time': '14:00',
                        'end_time': '18:00'
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
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi',
        'Sunday': 'Dimanche'
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
            return redirect('schedule:course_list')
    else:
        form = CourseScheduleForm(instance=schedule)

    return render(request, 'schedule/edit_schedule.html', {
        'form': form,
        'schedule': schedule,
        'course': course
    })

@login_required
def create_work(request):
    # Vérifier si l'utilisateur est un CP
    if not hasattr(request.user, 'cpprofile'):
        return HttpResponseForbidden("Seuls les CP peuvent créer des TP.")

    if request.method == 'POST':
        form = WorkForm(request.POST, request.FILES, faculty=request.user.cpprofile.faculty)
        if form.is_valid():
            work = form.save()
            messages.success(request, 'Le TP a été créé avec succès.')
            return redirect('schedule:work_list')
    else:
        form = WorkForm(faculty=request.user.cpprofile.faculty)
    
    return render(request, 'schedule/create_work.html', {'form': form})

@login_required
def work_list(request):
    # Si c'est un CP, montrer les TPs de sa faculté
    if hasattr(request.user, 'cpprofile'):
        works = Work.objects.filter(
            course__faculty=request.user.cpprofile.faculty,
            due_date__gte=timezone.now()
        ).order_by('due_date')
    # Si c'est un étudiant, montrer les TPs de sa faculté
    elif hasattr(request.user, 'student'):
        works = Work.objects.filter(
            course__faculty=request.user.student.faculty,
            due_date__gte=timezone.now()
        ).order_by('due_date')
    else:
        works = []
    
    return render(request, 'schedule/work_list.html', {'works': works})
