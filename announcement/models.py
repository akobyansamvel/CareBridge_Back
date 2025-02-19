# announcement/models.py

from django.db import models
from authentication.models import User

class Announcement(models.Model):
    URGENCY_CHOICES = [
        ('Срочно', 'Срочно'),
        ('Не особо срочно', 'Не особо срочно'),
        ('Выбор времени', 'Выбор времени'),
    ]
    
    TASK_CHOICES = [
        ('Ремонт', 'Ремонт'),
        ('Покупки', 'Покупки'),
        ('Уборка', 'Уборка'),
        ('Слушатель', 'Слушатель'),
        ('Другое', 'Другое'),
    ]
    
    GENDER_CHOICES = [
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
        ('Не важно', 'Не важно'),
    ]
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    # geolocation = models.CharField(max_length=255, verbose_name='Геоданные')
    task_type = models.CharField(max_length=50, choices=TASK_CHOICES, verbose_name='Тип задания')
    preferred_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, verbose_name='Предпочитаемый пол')
    urgency = models.CharField(max_length=50, choices=URGENCY_CHOICES, verbose_name='Срочность')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class VolunteerResponse(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="responses")
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="volunteer_responses")
    response_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response from {self.volunteer} to {self.announcement.title}"
