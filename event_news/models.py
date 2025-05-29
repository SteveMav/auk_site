from django.db import models
from django.contrib.auth.models import User
from schedule.models import Faculty

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='event_participants')

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_news:event_detail', args=[str(self.id)])

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.FileField(upload_to='news_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    target_faculties = models.ManyToManyField(Faculty, related_name='news', blank=True)
    is_public = models.BooleanField(default=False, help_text="Si activé, la news sera visible par tous les étudiants indépendamment de leur faculté")

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_news:news_detail', args=[str(self.id)])
