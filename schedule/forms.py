from django import forms
from .models import Course, Faculty

DAYS_OF_WEEK = [
    ('Monday', 'Lundi'),
    ('Tuesday', 'Mardi'),
    ('Wednesday', 'Mercredi'),
    ('Thursday', 'Jeudi'),
    ('Friday', 'Vendredi'),
    ('Saturday', 'Samedi'),
    ('Sunday', 'Dimanche'),
]

class CourseWithScheduleForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    professor = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    total_hours = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    finished = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # Champs horaires par jour
    for day, label in DAYS_OF_WEEK:
        locals()[f'{day}_start'] = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), label=f"{label} - Début")
        locals()[f'{day}_end'] = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), label=f"{label} - Fin")
