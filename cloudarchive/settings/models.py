from django.db import models
from django.contrib.auth.models import User

class Settings(models.Model):
    user = models.UUIDField(default='')
    theme = models.CharField(max_length=10, default='DARK')  # Тема
    notifications = models.BooleanField(default=True)        # Уведомления
    display_mode = models.CharField(max_length=10, default='GRID')  # Режим отображения
    language = models.CharField(max_length=10, default='RU')  # Язык интерфейса
    storage_alert = models.BooleanField(default=True)  # Оповещение о заполнении хранилища
