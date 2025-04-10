from django.shortcuts import render, redirect
from .forms import CourseForm
from .models import Course, CourseSchedule

def create_course(request):
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            # On récupère les horaires via JS (JSON dans un champ caché)
            import json
            schedule_data = json.loads(request.POST.get('schedules', '{}'))
            for day, blocks in schedule_data.items():
                if 'morning' in blocks:
                    CourseSchedule.objects.create(course=course, day_of_week=day, start_time='08:00', end_time='12:00')
                if 'afternoon' in blocks:
                    CourseSchedule.objects.create(course=course, day_of_week=day, start_time='14:00', end_time='18:00')
            return redirect('schedule:course_list')
    else:
        form = CourseForm()
    return render(request, 'schedule/create_course.html', {'form': form, 'days': days})


def course_list(request):
    courses = Course.objects.all().prefetch_related('courseschedule_set')
    return render(request, 'schedule/course_list.html', {'courses': courses})
