import requests

# # Параметры запроса
# unique_name = "views(1).py"  # Замените на фактическое имя файла
# original_filename = "views.py"  # Замените на имя, которое нужно сохранить при скачивании

# # URL вашего API
# url = f"http://localhost:8002/files/{unique_name}"
# params = {'original_filename': original_filename}  # Параметр запроса

# # Выполнение GET запроса с параметрами
# response = requests.get(url, params=params)

# # Проверка ответа
# if response.status_code == 200:
#     # Сохранение файла
#     print(f"Файл '{original_filename}' успешно загружен!")
# else:
#     # Печать текстового содержимого ответа при ошибке
#     print(f"Ошибка {response.status_code}: {response.text}"

response = requests.get('http://127.0.0.1:8000/get_size/', params={'user': 'fortex'})
print(response.json())