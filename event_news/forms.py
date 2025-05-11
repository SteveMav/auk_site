from django import forms
from .models import News, Event

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'target_faculties', 'is_public']
        labels = {
            'title': 'Titre',
            'content': 'Contenu',
            'image': 'Image',
            'target_faculties': 'Facultés ciblées',
            'is_public': 'Visible par tous'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'target_faculties': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_faculties'].required = False  # Rendre le champ facultatif

class EventForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location']
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'location': 'Lieu'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'})
        }