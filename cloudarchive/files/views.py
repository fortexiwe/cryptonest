from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseRedirect, FileResponse
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import FileUpload, generate_unique_filename, Folder, FilesSize
import requests
import os
from regauth.models import User
from regauth.utils import authorized_required
from django.shortcuts import get_object_or_404
from zipfile import ZipFile
import os
import io
# from .ai import generate_image



ARCHIVE_URL: str = 'http://0.0.0.0:8001/archive/'


"""
    Функция, которая позволяет загрузить файл:
    1. Есть возможность выбрать архивирование или обычную загрузку
        при архивировании файл улетает на сервак с архивацией, а после улетает на сервер хранения
    2. При обычной загрузке файл сразу улетает на сервер хранения
"""
@authorized_required
def upload_file(request):
    if request.method == 'POST' and 'files' in request.FILES:
        uploaded_files = request.FILES.getlist('files')
        upload_type = request.POST.get('upload_type')
        folder_id = request.POST.get('folder')
        folder = Folder.objects.filter(id=folder_id).first() if folder_id else None

        if not upload_type:
            return render(request, 'upload.html', {'error_message': 'Выберите тип загрузки'})

        try:
            file_records = []
            cached_files = cache.get('file_list') or []
            
            for uploaded_file in uploaded_files:
                original_filename = uploaded_file.name
                unique_filename = generate_unique_filename(None, original_filename)
                # Читаем содержимое файла один раз и сохраняем его в переменную
                file_content = uploaded_file.read()
                # Если выбрано Архивирование, отправляем файл напрямую на сервер архивации
                if upload_type == "Архивирование":
                    files = {'files': (unique_filename, file_content)}  
                    
                    password = request.POST.get('password')
                    
                    # Отправляем запрос на архивацию
                    response = requests.post(ARCHIVE_URL, files=files, data={'password': password, 'user': request.session['username']})

                    if response.status_code == 200:
                        archive_filename = response.json().get('archive_filename')
                        archive_path = response.json().get('archive_path')

                        
                        file_record = FileUpload.objects.create(
                            user=request.session['id'],
                            original_filename=archive_filename,
                            stored_filename=unique_filename,
                            file=archive_path,
                            folder=folder
                        )
                    else:
                        error_message = f"Ошибка архивации: {response.status_code}, {response.text}"
                        print(error_message)
                        return JsonResponse({'status': 'error', 'message': error_message}, status=500)
                else:
                    saved_path = default_storage.save(unique_filename, uploaded_file)
                    # Сохраняем файл на сервере хранения
                    files_to_send = {'files': (unique_filename, file_content)}
                    data = request.POST.get('password')  
                    response = requests.post('http://0.0.0.0:8002/cloud/', files=files_to_send, data={'password': data, 'user': request.session['username']})

                    if response.status_code != 200:
                        error_message = f"Ошибка при отправке файла: {response.status_code}, {response.text}"
                        print(error_message)
                        return JsonResponse({'status': 'error', 'message': error_message}, status=500)

                    file_record = FileUpload.objects.create(
                        user=request.session['id'],
                        original_filename=original_filename,
                        stored_filename=unique_filename,
                        file=saved_path,
                        folder=folder
                    )

                # Обновление кэша
                cached_files.append({
                    'name': original_filename,
                    'extension': os.path.splitext(original_filename)[1][1:],
                    'is_image': file_record.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')),
                    'time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                })

                file_records.append(file_record)

            cache.set('file_list', cached_files, timeout=1000000)
            return render(request, 'afterload.html', context={'files': [{'file_id': f.id, 'original_filename': f.original_filename} for f in file_records]})


        except Exception as e:
            print(f"Ошибка при загрузке файлов: {e}")
            return JsonResponse({'status': 'error', 'message': 'Ошибка при загрузке файлов.'}, status=500)

    return render(request, 'upload.html', context={
        'folders': Folder.objects.filter(user=request.session['id'])
    })


"""
    Обращается на сервер хранения, если там есть такой файл, то скачивает его
"""
def download_file(request, file_id):
    try:
        # Ищем файл по id
        file_record = FileUpload.objects.get(id=file_id)
        unique_name = file_record.stored_filename
        password = request.POST.get('password')
        

        # Запрос к серверу для получения файла
        response = requests.get(
            f'http://0.0.0.0:8002/files/{unique_name}/',
            params={'original_filename': file_record.original_filename, 'password': password}
        )
        # Если вернулась 404, то пробуем сделать еще один запрос но с другим расширением файла
        if response.status_code == 404:
            new_extension = '.zip'
            base_name = os.path.splitext(unique_name)[0]
            new_filename = base_name + new_extension
            response = requests.get(
            f'http://0.0.0.0:8002/files/{new_filename}/',
            params={'original_filename': file_record.original_filename, 'password': password}
        )


        if response.status_code == 200:
            # Создаем response из полученных данных
            response = HttpResponse(
                response.content,
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{file_record.original_filename}"'
            return response
        else:

            raise Http404("Файл не найден на сервере")
    except FileUpload.DoesNotExist:
        raise Http404("Файл не найден в базе данных")
    

def download_selected_files(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('selected_files')
        if not file_ids:
            return HttpResponse("Файлы не выбраны.", status=400)

        # Создаем временный архив
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for file_id in file_ids:
                file_obj = get_object_or_404(FileUpload, id=file_id)
                file_path = file_obj.file.path
                file_name = os.path.basename(file_path)
                zip_file.write(file_path, file_name)

        zip_buffer.seek(0)
        response = FileResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="selected_files.zip"'
        return response
    return HttpResponse("Метод не поддерживается.", status=405)





def cache_info(request):
    # Получаем кэшированные данные из Redis
    cached_files = cache.get('file_list')
    cache_time = cache.get('cache_time')

    # Если данных в кэше нет
    if cached_files is None:
        cached_files = []
        cache_time = "Данные еще не кэшированы."

    # Фильтрация по дате, если форма была отправлена
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            # Преобразуем строки в объекты datetime
            start_date = parse_datetime(start_date)
            end_date = parse_datetime(end_date)

            filtered_files = [
                file for file in cached_files
                if start_date <= file['timestamp'] <= end_date
            ]
            cached_files = filtered_files
            cache_time = f"Логи за период с {start_date} по {end_date}"

    
    paginator = Paginator(cached_files, 3)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

  
    return render(request, 'cache_info.html', context={
        'files': page_obj, 
        'cache_time': cache_time,
        'paginator': paginator,  
        'page_obj': page_obj  
    })

def transfer_file(request):
    folder = request.POST.get('folder')
    file = request.POST.get('file')
    FileUpload.objects.filter(original_filename=file).update(folder=folder)
    return render(request, 'transfer.html', context={'files': FileUpload.objects.filter(user=request.session['id']),
                                                     'folders': Folder.objects.filter(user=request.session['id'])})



"""Функция удаления файлов из БД"""
@authorized_required
def delete_file(request, file_id):
    try:
        FileUpload.objects.get(id=file_id).delete()
        return HttpResponseRedirect('/')
    except FileUpload.DoesNotExist:
        raise Http404
    

def rename_file(request, file_id):
    try:
        new_name = request.POST.get('name')
        FileUpload.objects.get(id=file_id).update(original_filename=new_name)
    except FileUpload.DoesNotExist:
        raise Http404


    
@csrf_exempt
def plus_size(request):
    # Получаем данные из POST-запроса
    user = request.POST.get('user')  # Получаем пользователя
    file_size = request.POST.get('file')  # Получаем размер файла

    # Проверяем, чтобы данные были
    if not user or not file_size:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        file_size = int(file_size)  # Преобразуем размер файла в целое число

        # Получаем текущий размер для пользователя
        file_size_object = FilesSize.objects.get(user=user)
        full_size = file_size_object.size

        # Обновляем размер
        full_size += file_size
        file_size_object.size = full_size
        file_size_object.save()
        

        return JsonResponse({'ok': 'ok'})
    except FilesSize.DoesNotExist:
        FilesSize.objects.create(user=user, size=file_size)
        return JsonResponse({'ok': 'ok'})
    except ValueError:
        return JsonResponse({'error': 'Invalid file size'}, status=400)
    

@csrf_exempt
def get_size(request):
    user = request.GET.get('user')  # Получаем имя пользователя из GET-запроса

    if not user:
        return JsonResponse({'error': 'User parameter is missing'}, status=400)

    try:
        # Получаем объект FilesSize или создаем новый, если его нет
        size_object, created = FilesSize.objects.get_or_create(user=user)

        # Если объект был создан, его размер будет 0
        return JsonResponse({'size': size_object.size})

    except FilesSize.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
