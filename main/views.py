from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, time, timedelta
from schedule.models import CourseSchedule
from event_news.models import News
from accounts.models import UserProfile
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q


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

    from datetime import timezone as dt_timezone, timedelta
    gmt1 = dt_timezone(timedelta(hours=1))
    current_time = timezone.now().astimezone(gmt1)
    print(current_time)
    # Conversion du jour anglais en français
    weekday_en_to_fr = {
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi',
        'Sunday': 'Dimanche',
    }
    current_weekday = weekday_en_to_fr[current_time.strftime('%A')]

    try:
        from accounts.models import UserProfile
        profile = UserProfile.objects.get(user=user)
        faculty = profile.faculty
    except Exception as e:
        logger.warning(f"Pas de UserProfile/faculty pour user {user}: {e}")
        return {'current_course': None, 'next_course': None, 'all_courses': []}

    # Récupère tous les cours du jour pour la faculty de l'utilisateur
    courses_today = CourseSchedule.objects.filter(
        course__faculty=faculty,
        day_of_week=current_weekday,
        course__finished=False
    ).order_by('start_time')

    logger.info(f"Cours trouvés pour {faculty} ({current_weekday}): {[str(c) for c in courses_today]}")

    current_course = None
    next_course = None
    from datetime import timedelta, datetime
    for course in courses_today:
        start = datetime.combine(current_time.date(), course.start_time, tzinfo=gmt1)
        end = datetime.combine(current_time.date(), course.end_time, tzinfo=gmt1) + timedelta(minutes=1) - timedelta(seconds=1)
        now = current_time
        if start <= now <= end:
            current_course = course
            break
    # 2. Si pas de cours en cours, cherche le prochain cours d'aujourd'hui
    if not current_course:
        for course in courses_today:
            if course.start_time > current_time.time():
                next_course = course
                break
    # 3. Si ni cours actuel ni prochain aujourd'hui, cherche le prochain cours tous jours confondus
    if not current_course and not next_course:
        all_next_courses = CourseSchedule.objects.filter(
            course__faculty=faculty,
            course__finished=False,
        ).order_by('day_of_week', 'start_time')
        from datetime import timedelta
        weekday_to_int = {
            'Lundi': 0, 'Mardi': 1, 'Mercredi': 2, 'Jeudi': 3,
            'Vendredi': 4, 'Samedi': 5, 'Dimanche': 6
        }
        now_weekday = current_time.weekday()
        now_time = current_time.time()
        soonest = None
        soonest_delta = None
        for sched in all_next_courses:
            sched_weekday = weekday_to_int[sched.day_of_week]
            days_ahead = (sched_weekday - now_weekday) % 7
            sched_datetime = (current_time + timedelta(days=days_ahead)).replace(
                hour=sched.start_time.hour,
                minute=sched.start_time.minute,
                second=0,
                microsecond=0
            )
            if days_ahead == 0 and sched.start_time <= now_time:
                continue
            delta = sched_datetime - current_time
            if soonest is None or delta < soonest_delta:
                soonest = sched
                soonest_delta = delta
        next_course = soonest
        if soonest:
            next_day = soonest.day_of_week
            courses_that_day = CourseSchedule.objects.filter(
                course__faculty=faculty,
                day_of_week=next_day,
                course__finished=False
            ).order_by('start_time')
        else:
            courses_that_day = []
        return {
            'current_course': None,
            'next_course': next_course,
            'all_courses': list(courses_that_day),
        }
    # 4. Si cours en cours, n'affiche PAS de next_course
    if current_course:
        return {
            'current_course': current_course,
            'next_course': None,
            'all_courses': list(courses_today),
        }
    # 5. Sinon (pas de cours en cours mais un prochain aujourd'hui)
    return {
        'current_course': None,
        'next_course': next_course,
        'all_courses': list(courses_today),
    }

def index(request):
    course_info = get_user_courses(request.user)
    latest_news = News.objects.all()[:3]
    return render(request, 'home/index.html', {
        'course_info': course_info,
        'latest_news': latest_news,
    })

@user_passes_test(lambda u: u.is_superuser)
def all_students_view(request):
    q = request.GET.get('q', '').strip()
    faculty_id = request.GET.get('faculty', '')
    students = UserProfile.objects.select_related('user', 'faculty').all()
    if q:
        students = students.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
    if faculty_id:
        students = students.filter(faculty_id=faculty_id)
    students = students.order_by('faculty__name', 'user__last_name', 'user__first_name')
    # Comptage par faculté
    faculty_counts = UserProfile.objects.values('faculty__id','faculty__name').annotate(count=Count('id')).order_by('faculty__name')
    from schedule.models import Faculty
    faculties = Faculty.objects.all()
    students_total = UserProfile.objects.count()
    return render(request, 'main/all_students.html', {
        'students': students,
        'faculty_counts': faculty_counts,
        'faculties': faculties,
        'q': q,
        'faculty_id': faculty_id,
        'students_total': students_total,
    })

