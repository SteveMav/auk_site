from django.shortcuts import render, redirect
from .forms import CourseForm, MultiScheduleForm
from .models import Course, CourseSchedule

def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('schedule:course_list')
    else:
        form = CourseForm()
    return render(request, 'schedule/create_course.html', {'form': form})

def create_schedule(request):
    if request.method == 'POST':
        form = MultiScheduleForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            days = form.cleaned_data['days']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            # Crée un CourseSchedule pour chaque jour sélectionné
            for day in days:
                CourseSchedule.objects.create(
                    course=course,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time
                )
            return redirect('schedule:course_list')
    else:
        form = MultiScheduleForm()
    return render(request, 'schedule/create_schedule.html', {'form': form})



def course_list(request):
    courses = Course.objects.all().prefetch_related('courseschedule_set')
    return render(request, 'schedule/course_list.html', {'courses': courses})
