from django.db import models
from uuid import uuid4


def upload_to(instance, filename):
    """
    Функция для определения пути сохранения файлов.
    Если файл принадлежит определённой папке, он будет сохранён в подпапке с названием этой папки.
    Пример: uploads/<folder_name>/<filename>
    """
    folder_name = instance.folder.name if instance.folder else "default"
    return f"uploads/{folder_name}/{filename}"


class User(models.Model):
    id       = models.UUIDField(default=uuid4, primary_key=True)
    email    = models.CharField(max_length=128, blank=False, unique=True)
    username = models.CharField(max_length=32, blank=False)
    password = models.CharField(max_length=128, blank=False)
    
    
    


    def __str__(self) -> str:
        return self.username


class UserProfile(models.Model):
    username = models.CharField(max_length=32, blank=False)
    image = models.TextField(blank=True)


class BuyGB(models.Model):
    id_user = models.CharField(max_length=1024)
    GB = models.IntegerField(default=0)