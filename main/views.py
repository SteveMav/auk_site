from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, time
from schedule.models import CourseSchedule
from event_news.models import News

def get_current_or_next_course(user):
    if not user.is_authenticated:
        return None
        
    current_time = timezone.localtime()
    current_weekday = current_time.strftime('%A')
    
    # Get student's faculty
    try:
        student = user.student
        faculty = student.faculty
    except:
        return None

    # Find current course
    current_course = CourseSchedule.objects.filter(
        course__faculty=faculty,
        day_of_week=current_weekday,
        start_time__lte=current_time.time(),
        end_time__gte=current_time.time(),
        course__finished=False
    ).first()
    
    if current_course:
        return {'course': current_course, 'status': 'current'}
    
    # If no current course, find next course today
    next_course = CourseSchedule.objects.filter(
        course__faculty=faculty,
        day_of_week=current_weekday,
        start_time__gt=current_time.time(),
        course__finished=False
    ).order_by('start_time').first()
    
    if next_course:
        return {'course': next_course, 'status': 'next'}
    
    return None

def index(request):
    course_info = get_current_or_next_course(request.user)
    
    # Debug: afficher toutes les news
    all_news = News.objects.all()
    
    latest_news = all_news[:2]  # Get the 2 most recent news
    return render(request, 'home/index.html', {
        'course_info': course_info,
        'latest_news': latest_news,
    })
