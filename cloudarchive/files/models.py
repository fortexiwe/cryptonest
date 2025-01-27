from django.db import models
import uuid
from pathlib import Path
from regauth.models import User

def generate_unique_filename(instance, filename):
    extension = filename.split('.')[-1]
    unique_name = f'{uuid.uuid4()}.{extension}'
    return unique_name



import uuid
from pathlib import Path
from django.db import models


class Folder(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.UUIDField(default='')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def upload_to(instance, filename):
    """
    Функция для определения пути сохранения файлов.
    Если файл принадлежит определённой папке, он будет сохранён в подпапке с названием этой папки.
    Пример: uploads/<folder_name>/<filename>
    """
    folder_name = instance.folder.name if instance.folder else "default"
    return f"uploads/{folder_name}/{filename}"


class FileUpload(models.Model):
    user = models.UUIDField(default='')
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255, unique=True)
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='files'
    )
    file = models.FileField(upload_to=upload_to)  # Путь к файлу через функцию upload_to
    created_at = models.DateTimeField(auto_now_add=True)
    extension = models.CharField(max_length=10, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Устанавливаем расширение файла перед сохранением
        if not self.extension:
            file_path = Path(self.file.name)
            self.extension = file_path.suffix[1:].lower()  # Извлекаем расширение без точки

        # Устанавливаем stored_filename, если он не указан
        if not self.stored_filename:
            self.stored_filename = self.file.name

        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_filename
    

class FilesSize(models.Model):
    user = models.CharField(max_length=128, blank=True)
    size = models.IntegerField(default=0)
