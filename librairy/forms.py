from django import forms
from .models import Article, Books

from django.forms.widgets import TextInput

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image', 'files']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['title', 'author', 'description', 'image', 'files']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'author': TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
