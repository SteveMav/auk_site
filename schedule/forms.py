from django import forms
from django.core.exceptions import ValidationError
from .models import Course, CourseSchedule

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'professor', 'total_hours', 'faculty', 'finished']

class CourseScheduleForm(forms.ModelForm):
    class Meta:
        model = CourseSchedule
        fields = ['course', 'day_of_week', 'start_time', 'end_time']

    def clean(self):
        cleaned_data = super().clean()
        day_of_week = cleaned_data.get('day_of_week')
        course = cleaned_data.get('course')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if all([day_of_week, course, start_time, end_time]):
            faculty = course.faculty
            
            # Déterminer le créneau horaire (matin ou après-midi)
            is_morning = start_time.hour < 12
            time_slot = 'matin' if is_morning else 'après-midi'
            
            # Vérifier s'il existe déjà un cours dans le même créneau
            existing_schedules = CourseSchedule.objects.filter(
                course__faculty=faculty,
                day_of_week=day_of_week
            ).exclude(id=self.instance.id if self.instance else None)
            
            # Compter les cours dans le même créneau horaire
            same_slot_count = sum(
                1 for schedule in existing_schedules
                if (schedule.start_time.hour < 12) == is_morning
            )
            
            if same_slot_count >= 1:
                raise ValidationError(
                    f'Il ne peut pas y avoir plus d\'un cours par créneau horaire. '
                    f'La faculté {faculty.name} a déjà un cours programmé le {day_of_week} {time_slot}.'
                )
            
            # Vérifier le nombre total de cours par jour
            if existing_schedules.count() >= 2:
                raise ValidationError(
                    'Il ne peut pas y avoir plus de 2 cours par jour pour une même faculté. '
                    f'La faculté {faculty.name} a déjà 2 cours programmés le {day_of_week}.'
                )

        return cleaned_data
