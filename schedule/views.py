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
    cp_profile = CPProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)

            # Empêcher la création pour une autre faculté
            if course.faculty != cp_profile.faculty:
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
        form.fields['faculty'].queryset = form.fields['faculty'].queryset.filter(id=cp_profile.faculty.id)

    return render(request, 'schedule/create_course.html', {'form': form, 'days': days})



@login_required
def course_list(request):
    courses = Course.objects.all().prefetch_related('courseschedule_set')
    return render(request, 'schedule/course_list.html', {'courses': courses})
