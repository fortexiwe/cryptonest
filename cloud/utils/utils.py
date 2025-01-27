from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from os import urandom

# Преобразование строки пароля в ключ
def derive_key_from_string(password_str, salt):
    password_bytes = password_str.encode()  # Преобразование строки в байты
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 байта для AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password_bytes)
    return key

# Функция шифрования содержимого файла в том же месте
def encrypt_file_content(input_file_path, password_str):
    with open(input_file_path, 'rb') as f:
        file_data = f.read()

    salt = urandom(16)  # Генерация соли
    iv = urandom(16)  # Генерация вектора инициализации (IV)

    # Воссоздание ключа из пароля и соли
    key = derive_key_from_string(password_str, salt)

    # Настройка шифра AES с новым IV и режимом CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Выравнивание данных (padding)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_data) + padder.finalize()

    # Шифрование данных
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Перезапись зашифрованных данных в файл, сохраняя соль и IV в начале
    with open(input_file_path, 'wb') as f:
        f.write(salt + iv + encrypted_data)

    return input_file_path



def decrypt_file_content(file_path, password_str):
    # Открытие зашифрованного файла
    with open(file_path, 'rb') as f:
        salt = f.read(16)  # Первая часть файла - соль
        iv = f.read(16)  # Далее - вектор инициализации (IV)
        encrypted_data = f.read()  # Зашифрованные данные

    # Генерация ключа на основе пароля и соли
    key = derive_key_from_string(password_str, salt)  # Получаем ключ из пароля и соли

    # Проверка типа ключа
    if not isinstance(key, bytes):
        raise TypeError("Derived key must be bytes-like")

    # Настройка шифра AES с тем же IV и режимом CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Расшифровка данных
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Удаление выравнивания (unpadding)
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    # Возвращаем расшифрованные данные, не изменяя зашифрованный файл
    return data

