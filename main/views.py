from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, time, timedelta
from schedule.models import CourseSchedule
from event_news.models import News

def get_user_courses(user):
    """
    Retourne un dictionnaire avec :
      - current_course : le cours en cours (None si aucun)
      - next_course : le prochain cours de la journée (None si aucun)
      - all_courses : tous les cours du jour (ordre horaire)
    """
    import logging
    logger = logging.getLogger("main.views")

    if not user.is_authenticated:
        return {'current_course': None, 'next_course': None, 'all_courses': []}

    current_time = timezone.localtime()
    current_weekday = current_time.strftime('%A')

    try:
        from accounts.models import UserProfile
        profile = UserProfile.objects.get(user=user)
        faculty = profile.faculty
    except Exception as e:
        logger.warning(f"Pas de UserProfile/faculty pour user {user}: {e}")
        return {'current_course': None, 'next_course': None, 'all_courses': []}

    # Récupère tous les cours du jour pour la faculty de l'utilisateur
    courses = CourseSchedule.objects.filter(
        course__faculty=faculty,
        day_of_week=current_weekday,
        course__finished=False
    ).order_by('start_time')

    logger.info(f"Cours trouvés pour {faculty} ({current_weekday}): {[str(c) for c in courses]}")

    current_course = None
    next_course = None
    for course in courses:
        if course.start_time <= current_time.time() <= course.end_time:
            current_course = course
            break  # On prend le premier qui correspond
    if not current_course:
        for course in courses:
            if course.start_time > current_time.time():
                next_course = course
                break
    return {
        'current_course': current_course,
        'next_course': next_course,
        'all_courses': list(courses),
    }

def index(request):
    course_info = get_user_courses(request.user)
    print(course_info)
    latest_news = News.objects.all()[:3]
    return render(request, 'home/index.html', {
        'course_info': course_info,
        'latest_news': latest_news,
    })

# from pprint import pprint

# def index(request):
#     course_info = get_user_courses(request.user)
#     latest_news = News.objects.all()[:3]

#     # DEBUG : Afficher tous les CourseSchedule du jour
#     current_time = timezone.localtime()
#     current_weekday = current_time.strftime('%A')
#     all_sched = CourseSchedule.objects.filter(day_of_week=current_weekday)
#     print(f"DEBUG - Schedules pour {current_weekday}:")
#     for sched in all_sched:
#         print(f"  - {sched} | faculty: {sched.course.faculty} | finished: {sched.course.finished}")

#     # DEBUG : Afficher student + faculty
#     if request.user.is_authenticated:
#         try:
#             print(f"DEBUG - Student: {request.user.student} | faculty: {request.user.student.faculty}")
#         except Exception as e:
#             print(f"DEBUG - Pas de student pour user: {e}")

#     return render(request, 'home/index.html', {
#         'course_info': course_info,
#         'latest_news': latest_news,
#     })