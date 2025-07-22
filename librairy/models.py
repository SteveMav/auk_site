from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    files = models.FileField(upload_to='articles/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('librairy:article_detail', args=[str(self.id)])

class Books(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE)
    files = models.FileField(upload_to='books/')
    description = models.TextField(blank=True, null=True)
    date_published = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('librairy:book_detail', args=[str(self.id)])

    

