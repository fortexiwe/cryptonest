from django.shortcuts import render
from .ai import generate_image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import speech_recognition as sr
import subprocess
import os


@csrf_exempt
def image(request):
    """
    Обработчик запросов для генерации изображений по текстовому или голосовому вводу.
    """
    if request.method == 'POST':
        # Получение текстового ввода
        prompt = request.POST.get('prompt', '')

        # Если текстового ввода нет, обработать голосовой ввод
        if not prompt and 'voice_prompt' in request.FILES:
            voice_file = request.FILES['voice_prompt']
            prompt = process_voice_input(voice_file)  # Функция для обработки голосового ввода

        if prompt:
            # Генерация изображения и конвертация в base64
            img_str = generate_image(prompt)
            return render(request, 'image_result.html', {'img_str': img_str, 'prompt': prompt})
        else:
            return render(request, 'image_input.html', {'error': 'Пожалуйста, введите текст или загрузите аудио.'})

    return render(request, 'image_input.html')



def process_voice_input(voice_file):
    """
    Обрабатывает загруженный аудиофайл и преобразует его в текст.
    """
    # Пути для временных файлов
    input_path = 'temp_uploaded_audio.webm'
    output_path = 'temp_audio.wav'

    try:
        # Сохранение загруженного файла
        with open(input_path, 'wb') as f:
            for chunk in voice_file.chunks():
                f.write(chunk)

        # Конвертация файла в WAV
        subprocess.run(
            ['ffmpeg', '-i', input_path, '-ar', '16000', '-ac', '1', output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Распознавание речи
        recognizer = sr.Recognizer()
        with sr.AudioFile(output_path) as source:
            audio = recognizer.record(source)

        # Преобразование аудио в текст
        text = recognizer.recognize_google(audio, language='ru-RU')
        return text

    except subprocess.CalledProcessError as e:
        return f"Ошибка конвертации аудио: {e}"
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка службы распознавания: {e}"
    except Exception as e:
        return f"Произошла ошибка: {e}"
    finally:
        # Удаление временных файлов
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
