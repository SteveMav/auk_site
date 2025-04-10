from django import forms
from .models import Course

# DAYS_OF_WEEK = [
#     ('Monday', 'Lundi'),
#     ('Tuesday', 'Mardi'),
#     ('Wednesday', 'Mercredi'),
#     ('Thursday', 'Jeudi'),
#     ('Friday', 'Vendredi'),
#     ('Saturday', 'Samedi'),
#     ('Sunday', 'Dimanche'),
# ]

# TIME_BLOCKS = [
#     ('morning', 'Matin (8h-12h)'),
#     ('afternoon', 'Après-midi (14h-18h)'),
#     ('both', 'Les deux'),
# ]

# class CourseForm(forms.ModelForm):
#     days = forms.MultipleChoiceField(
#         choices=DAYS_OF_WEEK,
#         widget=forms.CheckboxSelectMultiple,
#         label="Jours de cours"
#     )
#     schedule = forms.MultipleChoiceField(
#         choices=TIME_BLOCKS,
#         widget=forms.CheckboxSelectMultiple,
#         label="Créneau horaire"
#     )

#     class Meta:
#         model = Course
#         fields = ['name', 'professor', 'total_hours', 'faculty', 'finished']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'professor', 'total_hours', 'faculty', 'finished']
