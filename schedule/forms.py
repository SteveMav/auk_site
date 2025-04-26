from django import forms
from django.core.exceptions import ValidationError
from .models import Course, CourseSchedule, Work, CourseFile, Exam

class CourseFileForm(forms.ModelForm):
    class Meta:
        model = CourseFile
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description du fichier (optionnel)'}),
        }

class CourseFileMultipleForm(forms.Form):
    files = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=True)
    description = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description commune (optionnel)'}))

class CourseForm(forms.ModelForm):
    pdf_file = forms.FileField(required=False, label='PDF du cours (optionnel)', widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Course
        fields = ['name', 'professor', 'total_hours', 'faculty', 'finished']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du cours'}),
            'professor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Professeur'}),
            'total_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Heures totales'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'finished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CourseScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['day_of_week'].choices = [
            ('Lundi', 'Lundi'),
            ('Mardi', 'Mardi'),
            ('Mercredi', 'Mercredi'),
            ('Jeudi', 'Jeudi'),
            ('Vendredi', 'Vendredi'),
            ('Samedi', 'Samedi'),
            ('Dimanche', 'Dimanche'),
        ]
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

class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'type', 'description', 'due_date', 'course', 'file']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        if faculty:
            self.fields['course'].queryset = Course.objects.filter(faculty=faculty, finished=False)
        # Ajoute la classe Bootstrap à tous les champs (sauf Checkbox/Radio)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing_classes + ' form-control custom-field').strip()

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Semestre'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salle ou lieu'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajoute la classe Bootstrap à tous les champs (sauf Checkbox/Radio)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing_classes + ' form-control custom-field').strip()
