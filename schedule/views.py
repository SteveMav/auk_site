from django.contrib.auth.forms import User
from django.shortcuts import render, redirect
from .forms import CourseForm
from .models import Course, CourseSchedule
from .models import CPProfile
from django.contrib.auth.decorators import login_required, permission_required
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

            # Création des horaires
            schedule_data = json.loads(request.POST.get('schedules', '{}'))
            for day, blocks in schedule_data.items():
                if 'morning' in blocks:
                    CourseSchedule.objects.create(course=course, day_of_week=day, start_time='08:00', end_time='12:00')
                if 'afternoon' in blocks:
                    CourseSchedule.objects.create(course=course, day_of_week=day, start_time='14:00', end_time='18:00')

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


