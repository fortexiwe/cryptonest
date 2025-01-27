from django.shortcuts import render
from .models import Settings


def settings(request):
    theme = request.POST.get('theme')
    notifications = request.POST.get('notifications') == 'on'
    display_mode = request.POST.get('display_mode')
    language = request.POST.get('language')
    storage_alert = request.POST.get('storage_alert') == 'on'

    if theme or display_mode or language or storage_alert:
        # Удаляем старые настройки, если они существуют
        try:
            Settings.objects.filter(user=request.session['id']).delete()

            # Создаем новую запись с настройками
            Settings.objects.create(
                user=request.session['id'],
                theme=theme,
                notifications=notifications,
                display_mode=display_mode,
                language=language,
                storage_alert=storage_alert
            )
        except:
            pass

    return render(request, 'settings.html')
