from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import login
from .models import User, UserProfile, BuyGB
from .forms import RegUserForm, AuthUserForm
from regauth.utils import authorized_required
from files.models import FileUpload, Folder
import requests
from django.core.mail import send_mail
from settings.models import Settings
import os
from django.contrib.auth import get_user_model
import string
from django.utils.crypto import get_random_string
from AI.ai import generate_image
from translate import Translator
from blockchain.models import Tokens


translator = Translator(to_lang="en")



FASTAPI_DRIVE = os.getenv('FASTAPI_DRIVE')


@authorized_required
def main_page(request):
    # GB = BuyGB.objects.get(id=request.session['id'])
    files = FileUpload.objects.filter(user=request.session['id'], folder__isnull=True)
    folders = Folder.objects.filter(user=request.session['id'])
    user_storage = get_user_storage(username=request.session['username'])
    user = UserProfile.objects.get(username=request.session['username'])
    try:

        settings = Settings.objects.get(user=request.session['id'])
        language = settings.language
        display_mode = settings.display_mode
    except:
        language = None
        display_mode = None

    
    storage_used = user_storage.get('storage_used_gb', 0)
    storage_total = user_storage.get('storage_total', 0) 
    storage_free = user_storage.get('storage_free', 0) #+ GB.GB

    used_percentage = (storage_used / storage_total * 100) if storage_total > 0 else 0
    total = user_storage.get('storage_total') #+ GB.GB

    try:
        theme = Settings.objects.get(user=request.session['id'])
        if theme.theme == 'WHITE':
            return render(request, 'index_white.html', context={
                'image' : user.image,
                'folders': folders,
                'files': files,
                'user_storage': user_storage,
                'used_percentage': used_percentage,
                'used': storage_used,
                'free': storage_free,
                'language': language,
                'display_mode': display_mode
                
            
            })
    except:
        pass

    return render(request, 'index.html', context={
        'image' : user.image,
        'folders': folders,
        'files': files,
        'user_storage': user_storage,
        'used_percentage': used_percentage,
        'used': float(storage_used),
        'free': storage_free,
        'language': language,
        'display_mode': display_mode,
        'total': total,
    })

def guest_page(request):
    context = {
        'reg_form': RegUserForm(),
        'auth_form': AuthUserForm(),
    }
    return render(request, 'guest.html', context=context)

def auth_page(request):
    if request.method == 'POST':
        form = AuthUserForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')

            try:
                user = User.objects.get(email=email, password=password)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not exist'})

            request.session['user_email'] = user.email
            request.session['id'] = user.id
            request.session['username'] = user.username
            return HttpResponseRedirect('/')
        else:
            return JsonResponse({'error': 'Form invalid'})
    else:
        return JsonResponse({'error': 'Method invalid'})

def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            Folder.objects.create(name=folder_name, user=request.session['id'])
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/')

def folder(request, folder_id):
    user = UserProfile.objects.get(username=request.session['username'])
    files = FileUpload.objects.filter(user=request.session['id'], folder=folder_id)
    folders = Folder.objects.filter(user=request.session['id'])
    user_storage = get_user_storage(username=request.session['username'])

    try:

        settings = Settings.objects.get(user=request.session['id'])
        language = settings.language
        display_mode = settings.display_mode
    except:
        language = None
        display_mode = None

    storage_used = user_storage.get('storage_used_gb', 0)
    storage_total = user_storage.get('storage_total', 0)
    storage_free = user_storage.get('storage_free', 0)

    used_percentage = (storage_used / storage_total * 100) if storage_total > 0 else 0

    return render(request, 'folder.html', context={
        'image': user.image,
        'folders': folders,
        'files': files,
        'user_storage': user_storage,
        'used_percentage': used_percentage,
        'used': storage_used,
        'free': storage_free,
        'language': language,
        'display_mode': display_mode
    })


User = get_user_model()

def reg_page(request):
    if request.method == 'POST':
        form = RegUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            avatar = form.cleaned_data['avatar']

            # Проверка существующих пользователей
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'User with this email already exists'})

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'})
            
            prompt = translator.translate(avatar)
            
            image = generate_image(prompt)

            # Создание пользователя
            user = User.objects.create(
                email=email,
                username=username,
                password=password,
            )
            UserProfile.objects.create(username=username, image=image)
            user.is_active = False  # Устанавливаем пользователя как неактивного
            user.save()

            verification_code = get_random_string(length=6, allowed_chars=string.ascii_uppercase + string.digits)

            request.session['verification_code'] = verification_code

            # Отправка письма с кодом подтверждения
            send_mail(
                'Код подтверждения регистрации',
                f'Ваш код подтверждения: {verification_code}',
                'fortexiwe@bk.ru', 
                [user.email],
                fail_silently=False,
            )

            # Сохранение данных пользователя в сессии для дальнейшего использования
            request.session['user_email'] = user.email
            request.session['id'] = user.id
            request.session['username'] = user.username

            return JsonResponse({'success': 'Пожалуйста, проверьте свою почту для подтверждения регистрации.'})
        else:
            return JsonResponse({'error': 'Form invalid'})
    else:
        return JsonResponse({'error': 'Method invalid'})

def confirm_email(request):
    if request.method == 'POST':
        code = request.POST.get('code') 
        user_email = request.session.get('user_email')

        verification_code = request.session.get('verification_code')

        if verification_code and code == verification_code:
            user = User.objects.get(email=user_email)

            # Активируем пользователя
            user.is_active = True
            user.save()

            # Удаляем код подтверждения после успешной активации
            del request.session['verification_code']

            # Авторизуем пользователя
            login(request, user)

            return HttpResponseRedirect('/')  # Перенаправляем на главную страницу
        else:
            return JsonResponse({'error': 'Неверный код подтверждения'})

    return render(request, 'confirm_email.html')  # Страница для ввода кода

def deauth(request):
    request.session.clear()
    return HttpResponseRedirect('/guest')

def get_user_storage(username):
    """ Получает информацию о занятом месте пользователя через FastAPI """
    try:
        response = requests.get(f"http://0.0.0.0:8002/storage/{username}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "storage_used": 0, "storage_total": 0, "storage_free": 0}

def custom_404(request, exception):
    return render(request, '404.html', status=404)


def buy_GB(request):
    if request.method == 'POST':
        tokens = Tokens.objects.get(id=request.session['id'])
        try:
            user_GB = BuyGB.objects.get(id=request.session['id'])
        except BuyGB.DoesNotExist:
            user_GB = BuyGB.objects.create(id=request.session['id'], GB=0)

        GB = int(request.POST.get('GB', 0))
        price = GB * 10

        if tokens.NBM < price:
            return render(request, 'buy_gb.html', {
                'error_message': 'Недостаточно монет для покупки.'
            })

        # Обновляем монеты и гигабайты
        tokens.NBM -= price
        tokens.save()

        user_GB.GB += GB
        user_GB.save()

        return render(request, 'buy_gb.html', {
            'success_message': f'Вы успешно приобрели {GB} GB!',
        })

    return render(request, 'buy_gb.html')
