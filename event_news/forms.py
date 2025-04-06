from django import forms
from .models import News, Event

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image']
        labels = {
            'title': 'Titre',
            'content': 'Contenu',
            'image': 'Image'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

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