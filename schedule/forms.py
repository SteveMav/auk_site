from django import forms
from .models import Course, CourseSchedule

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'professor', 'total_hours', 'faculty', 'finished']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'professor': forms.TextInput(attrs={'class': 'form-control'}),
            'total_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'finished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

DAYS_OF_WEEK = [
    ('Monday', 'Lundi'),
    ('Tuesday', 'Mardi'),
    ('Wednesday', 'Mercredi'),
    ('Thursday', 'Jeudi'),
    ('Friday', 'Vendredi'),
    ('Saturday', 'Samedi'),
    ('Sunday', 'Dimanche'),
]

class MultiScheduleForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple(),
        label="Jours de la semaine"
    )
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))