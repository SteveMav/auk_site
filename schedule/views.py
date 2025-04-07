from django.shortcuts import render, redirect
from .forms import CourseWithScheduleForm
from .models import Course, CourseSchedule

def create_course_with_schedule(request):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    if request.method == 'POST':
        form = CourseWithScheduleForm(request.POST)
        if form.is_valid():
            course = Course.objects.create(
                name=form.cleaned_data['name'],
                professor=form.cleaned_data['professor'],
                total_hours=form.cleaned_data['total_hours'],
                faculty=form.cleaned_data['faculty'],
                finished=form.cleaned_data['finished']
            )
            for day in days:
                start = form.cleaned_data.get(f'{day}_start')
                end = form.cleaned_data.get(f'{day}_end')
                if start and end:
                    CourseSchedule.objects.create(
                        course=course,
                        day_of_week=day,
                        start_time=start,
                        end_time=end
                    )
            return redirect('schedule:course_list')
    else:
        form = CourseWithScheduleForm()

    return render(request, 'schedule/create_course.html', {'form': form, 'days': days})



def course_list(request):
    courses = Course.objects.all().prefetch_related('courseschedule_set')
    return render(request, 'schedule/course_list.html', {'courses': courses})
