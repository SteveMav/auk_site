from django.db import models
from django.contrib.auth.models import User
from schedule.models import Faculty
from django.utils import timezone
import random
import string

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    numero_matricule = models.CharField(max_length=20, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.faculty}"

class PendingRegistration(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    confirmation_code = models.CharField(max_length=6, editable=False, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)

    def generate_confirmation_code(self):
        # Générer un code numérique à 6 chiffres
        return ''.join(random.choices(string.digits, k=6))

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = self.generate_confirmation_code()
        if not self.expires_at:
            self.expires_at = self.created_at + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Pending registration for {self.email}"
