from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
from datetime import datetime
# Мусорная функция, надеюсь перейду к нормльной SEARCH_DIRECTORIES
def get_download_directory():
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    elif 'ANDROID_ROOT' in os.environ:  # Termux на Android
        return os.path.join(os.environ['HOME'], 'downloads')
    else:  # Другая платформа
        return os.path.join(os.environ['HOME'], 'Downloads')

# Функция генерации пары ключей RSA с использованием имени пользователя и текущей даты
def get_private_key_directory():
    """Определяет директорию для сохранения приватного ключа в зависимости от платформы."""
    if os.name == 'nt':  # Windows
        # Папка пользователя на Windows
        return os.path.expanduser("~")
    elif 'ANDROID_ROOT' in os.environ:  # Termux на Android
        # Папка Termux на Android
        return '/data/data/com.termux/files/home'
    else:  # Другие платформы
        # Папка по умолчанию на других системах
        return os.path.expanduser("~")

def get_public_key_directory():
    """Определяет директорию для сохранения публичного ключа в зависимости от платформы."""
    if os.name == 'nt':  # Windows
        # Папка "Загрузки" пользователя на Windows
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    elif 'ANDROID_ROOT' in os.environ:  # Termux на Android
        # Папка на Android для сохранения публичных ключей
        return '/sdcard/'
    else:  # Другие платформы
        return os.path.expanduser("~")

def info():
    info = """
    Пожалуйста, выберите действие:

    1. Сначала надо сгенерировать ключи, найти их в папке (будет написано) и отправить другу
    2. После получения ключа можно воспользоваться автосканом, если он не работает написать путь к ключу вручную
    3. Для шифрования текста лучше использовать GCM метод, тк он имеет поддержку мульти строк и шифрует до 64гб текста
    4. Чтобы обнулить программу удалите файл keys.json и по желанию ключи
    5. GitHub создателя: https://github.com/VLOD-ZDOV
    """
    print(info)

def generate_key_pair(username):
    """Генерация пары ключей RSA с использованием имени пользователя и текущей даты."""
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")

    # Определяем пути для сохранения ключей
    pub_dir = get_public_key_directory()  # Путь для публичного ключа
    priv_dir = get_private_key_directory()  # Путь для приватного ключа

    # Генерация имени файлов для ключей на основе имени пользователя и текущей даты
    priv_filename = os.path.join(priv_dir, f"RSA_{username}_priv_{current_time}.pem")
    pub_filename = os.path.join(pub_dir, f"RSA_{username}_pub_{current_time}.pem")

    # Генерация приватного ключа
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # Сохранение приватного ключа
    with open(priv_filename, 'wb') as priv_file:
        priv_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Получение публичного ключа
    public_key = private_key.public_key()

    # Сохранение публичного ключа
    with open(pub_filename, 'wb') as pub_file:
        pub_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print(f"Приватный ключ сохранен в: {priv_filename}")
    print(f"Публичный ключ сохранен в: {pub_filename}")

    return priv_filename, pub_filename
# Сохранение информации о ключах в JSON файл
def save_keys_to_json(username, pub_filename, priv_filename, json_file="keys.json"):
    key_data = {
        "username": username,
        "public_key_path": pub_filename,
        "private_key_path": priv_filename
    }

    # Проверка существования JSON-файла
    if os.path.exists(json_file):
        with open(json_file, 'r+') as file:
            try:
                data = json.load(file)

                # Если данные в JSON не являются списком, преобразуем их в список
                if isinstance(data, dict):
                    data = [data]
                elif not isinstance(data, list):
                    raise ValueError("Неверный формат JSON файла: ожидается список.")

            except json.JSONDecodeError:
                # Если файл пуст или поврежден, создаем новый список
                data = []

            data.append(key_data)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        # Если JSON-файл не существует, создаем новый файл со списком ключей
        with open(json_file, 'w') as file:
            json.dump([key_data], file, indent=4)
# Поиск публичного ключа в директории "Загрузки"


# Добавление ключа друга в JSON
# Общие директории для поиска ключей и зашифрованных файлов
if os.name == 'nt':  # Windows
    SEARCH_DIRECTORIES = [
        os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
        os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),
        os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')
    ]
if 'ANDROID_ROOT' in os.environ:  # Termux на Android
    SEARCH_DIRECTORIES = [
        '/data/data/com.termux/files/home/custom_keys',  # Пример: пользовательская папка в Termux
        '/sdcard/CustomKeys',  # Пример: пользовательская папка на Android
        '/sdcard/Download',  # Папка загрузок
        '/sdcard/Download/Telegram/',  # Папка Telegram
        '/sdcard/WhatsApp/Media/WhatsApp Documents'  # Папка WhatsApp
    ]
else:  # Другие платформы
    SEARCH_DIRECTORIES = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads")
    ]

def scan_for_public_keys(json_file):
    """Сканирует стандартные и дополнительные папки на наличие файлов с публичными ключами, исключая уже существующие в keys.json."""
    
    # Загружаем существующие ключи из JSON файла
    with open(json_file, 'r') as file:
        data = json.load(file)
        existing_keys = {entry.get('public_key_path') for entry in data if entry.get('public_key_path')}

    found_keys = set()

    # Поиск ключей во всех директориях из SEARCH_DIRECTORIES
    for dir_path in SEARCH_DIRECTORIES:
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for filename in files:
                    if filename.endswith('.pem') and 'pub' in filename:
                        key_path = os.path.join(root, filename)
                        key_path = os.path.normpath(key_path)  # Нормализуем путь
                        if key_path not in existing_keys:  # Проверяем, чтобы ключ не был уже добавлен
                            found_keys.add(key_path)

    return list(found_keys)  # Преобразуем set обратно в list

def scan_for_keys(json_file, key_type='public'):
    """
    Сканирует стандартные и дополнительные папки на наличие файлов ключей, исключая уже существующие в keys.json.
    key_type может быть 'public' или 'private'.
    """
    # Загружаем существующие ключи из JSON файла
    with open(json_file, 'r') as file:
        data = json.load(file)
        existing_keys = {entry.get(f'{key_type}_key_path') for entry in data if entry.get(f'{key_type}_key_path')}

    found_keys = set()

    # Поиск ключей во всех директориях из SEARCH_DIRECTORIES
    for dir_path in SEARCH_DIRECTORIES:
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for filename in files:
                    key_path = os.path.join(root, filename)
                    key_path = os.path.normpath(key_path)  # Нормализуем путь
                    
                    if (key_type == 'public' and filename.endswith('.pem') and 'pub' in filename) or \
                       (key_type == 'private' and filename.endswith('.pem') and 'pub' not in filename):
                        if key_path not in existing_keys:  # Проверяем, чтобы ключ не был уже добавлен
                            found_keys.add(key_path)

    return list(found_keys)  # Преобразуем set обратно в list




def prompt_add_found_keys(json_file="keys.json"):
    """Предлагает пользователю добавить найденные публичные ключи в JSON файл."""
    found_keys = scan_for_public_keys()
    if not found_keys:
        print("Публичные ключи не найдены в стандартных и пользовательских папках.")
        return

    for key_path in found_keys:
        # Извлекаем имя пользователя из имени файла ключа
        username = key_path.split('_')[-3]  # Предполагается, что имя в формате RSA_<username>_pub_*.pem
        print(f"Найден ключ пользователя '{username}': {key_path}")
        add = input(f"Добавить ключ пользователя '{username}'? (y/n): ")
        if add.lower() == 'y':
            add_friend_public_key(username, key_path, json_file)
def add_friend_public_key(username, friend_pub_key_path, json_file="keys.json"):
    """Добавляет публичный ключ друга в JSON файл."""
    friend_key_data = {
        "username": username,
        "public_key_path": friend_pub_key_path,
        "private_key_path": None
    }
def add_friend_key(username, key_path, key_type, json_file):
    """
    Функция для добавления публичного или приватного ключа пользователя.
    key_type должен быть 'public' или 'private'.
    """
    if key_type not in ['public', 'private']:
        print("Неверный тип ключа. Укажите 'public' или 'private'.")
        return

    # Чтение существующих данных из JSON
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Поиск пользователя
    user_entry = next((entry for entry in data if entry['username'] == username), None)

    if not user_entry:
        # Создаем новую запись, если пользователя нет
        user_entry = {'username': username}
        data.append(user_entry)

    # Добавление пути к ключу в зависимости от типа
    if key_type == 'public':
        user_entry['public_key_path'] = key_path
        print(f"Публичный ключ для '{username}' добавлен.")
    elif key_type == 'private':
        user_entry['private_key_path'] = key_path
        print(f"Приватный ключ для '{username}' добавлен.")

    # Сохранение обновленных данных в JSON
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)


def delete_user_from_json(username, json_file="keys.json"):
    if os.path.exists(json_file):
        with open(json_file, 'r+') as file:
            data = json.load(file)
            data = [entry for entry in data if entry["username"] != username]
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

        print(f"Пользователь '{username}' успешно удален из JSON файла.")
    else:
        print(f"JSON файл '{json_file}' не существует.")

# Функция расшифровки с выбором ключа

def print_menu():
    """Функция для вывода меню."""
    menu = """
    Пожалуйста, выберите действие:

    1. Создать пару ключей и сохранить в JSON
    2. Зашифровать текст c использованием RSA
    3. Расшифровать текст c использованием RSA
    4. Зашифровать текст c использованием AES-GCM
    5. Расшифровать текст c использованием AES-GCM
    6. Зашифровать файл c использованием RSA
    7. Расшифровать файл c использованием RSA
    8. Зашифровать файл c использованием AES-GCM
    9. Расшифровать файл c использованием AES-GCM
    10. Добавить публичный или приватный ключ
    11. Показать всех пользователей
    12. Удалить пользователя из JSON файла
    13. Автоскан ключей
    14. Info
    0. Выйти из программы
    """
    print(menu)



def get_user_to_decrypt(json_file):
    """Функция для выбора пользователя с приватным ключом для расшифровки."""
    with open(json_file, 'r') as file:
        data = json.load(file)
        # Отфильтровываем пользователей, у которых есть приватный ключ
        valid_users = [entry for entry in data if entry.get("private_key_path")]
        for idx, entry in enumerate(valid_users):
            print(f"{idx + 1}. {entry['username']}")

    # Запрос выбора пользователя
    choice = int(input("Выберите пользователя (введите номер): ")) - 1

    if choice < 0 or choice >= len(valid_users):
        print("Неверный выбор.")
        return None, None

    return valid_users[choice]['private_key_path'], valid_users[choice]
def get_user_to_encrypt(json_file):
    """Функция для выбора пользователя с публичным ключом для шифрования."""
    with open(json_file, 'r') as file:
        data = json.load(file)
        # Отфильтровываем пользователей, у которых есть публичный ключ
        valid_users = [entry for entry in data if entry.get("public_key_path")]
        for idx, entry in enumerate(valid_users):
            print(f"{idx + 1}. {entry['username']}")

    # Запрос выбора пользователя
    choice = int(input("Выберите пользователя (введите номер): ")) - 1

    if choice < 0 or choice >= len(valid_users):
        print("Неверный выбор.")
        return None, None

    return valid_users[choice]['public_key_path'], valid_users[choice]
    


def get_multiline_input():
    """Функция для получения многолинейного ввода текста от пользователя."""
    print("Введите ваш текст (нажмите Ctrl-D для Linux/Mac/Termux или Ctrl-Z для Windows для завершения ввода):")
    
    # Считывание текста построчно
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    
    # Объединение строк в единый текст
    return "\n".join(contents)

def encrypt_text_gcm(public_key_path, text):
    """Шифрование текста с использованием RSA + AES-GCM."""
    # Генерация случайного ключа для AES
    aes_key = os.urandom(32)  # 256-битный ключ для AES
    iv = os.urandom(12)  # Рекомендуемый размер для GCM IV - 96 бит (12 байт)

    # Создание шифра AES-GCM
    encryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # Шифрование текста
    ciphertext = encryptor.update(text.encode()) + encryptor.finalize()

    # Шифрование AES ключа с использованием RSA
    with open(public_key_path, 'rb') as pub_file:
        public_key = serialization.load_pem_public_key(pub_file.read(), backend=default_backend())

    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Создание словаря с зашифрованными данными
    encrypted_data = {
        'aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'tag': base64.b64encode(encryptor.tag).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
    }

    # Вывод данных для удобного копирования и вставки
    formatted_output = f"{{'aes_key': '{encrypted_data['aes_key']}', 'iv': '{encrypted_data['iv']}', 'tag': '{encrypted_data['tag']}', 'ciphertext': '{encrypted_data['ciphertext']}'}}"
    print("\nСкопируйте следующий блок для использования в функции дешифрования:")
    #print(formatted_output)

    return encrypted_data



def decrypt_text_gcm(private_key_path, encrypted_data):
    """Расшифровка текста с использованием RSA + AES-GCM."""
    # Декодирование данных из base64
    encrypted_aes_key = base64.b64decode(encrypted_data['aes_key'])
    iv = base64.b64decode(encrypted_data['iv'])
    tag = base64.b64decode(encrypted_data['tag'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])

    # Чтение приватного ключа RSA
    with open(private_key_path, 'rb') as priv_file:
        private_key = serialization.load_pem_private_key(
            priv_file.read(),
            password=None,
            backend=default_backend()
        )

    # Расшифровка AES ключа с использованием RSA
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Расшифровка текста с использованием AES-GCM
    decryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    decrypted_text = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_text.decode('utf-8')



def encrypt_text(public_key_path, text):
    """Шифрование текста с использованием публичного ключа RSA."""
    # Загрузка публичного ключа
    with open(public_key_path, 'rb') as pub_file:
        public_key = serialization.load_pem_public_key(pub_file.read(), backend=default_backend())

    # Шифрование текста с использованием RSA и OAEP
    encrypted = public_key.encrypt(
        text.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Кодирование зашифрованного текста в base64
    encrypted_base64 = base64.b64encode(encrypted).decode('utf-8')

    return encrypted_base64

def decrypt_text(private_key_path, encrypted_message):
    """Расшифровка текста с использованием приватного ключа RSA."""
    # Декодирование зашифрованного сообщения из base64
    encrypted_message_bytes = base64.b64decode(encrypted_message)

    # Чтение приватного ключа RSA
    with open(private_key_path, 'rb') as priv_file:
        private_key = serialization.load_pem_private_key(
            priv_file.read(),
            password=None,
            backend=default_backend()
        )

    # Расшифровка сообщения с использованием приватного ключа RSA
    decrypted_message = private_key.decrypt(
        encrypted_message_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_message.decode('utf-8')



def encrypt_file_gcm(public_key_path, file_path):
    """Шифрование файла с использованием RSA + AES-GCM."""
    # Генерация случайного ключа для AES
    aes_key = os.urandom(32)
    iv = os.urandom(12)

    # Создание шифра AES-GCM
    encryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # Чтение данных из файла
    with open(file_path, 'rb') as f:
        plaintext = f.read()

    # Шифрование данных
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Шифрование AES ключа с использованием RSA
    with open(public_key_path, 'rb') as pub_file:
        public_key = serialization.load_pem_public_key(pub_file.read(), backend=default_backend())

    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Сохранение зашифрованных данных в файл
    encrypted_file_path = file_path + ".enc"
    with open(encrypted_file_path, 'wb') as f:
        f.write(encrypted_aes_key + iv + encryptor.tag + ciphertext)

    return encrypted_file_path

def decrypt_file_gcm(private_key_path, encrypted_file_path):
    """Расшифровка файла с использованием RSA + AES-GCM."""
    # Чтение зашифрованного файла
    with open(encrypted_file_path, 'rb') as f:
        encrypted_aes_key = f.read(256)  # Длина зашифрованного ключа RSA
        iv = f.read(12)
        tag = f.read(16)
        ciphertext = f.read()

    # Чтение приватного ключа RSA
    with open(private_key_path, 'rb') as priv_file:
        private_key = serialization.load_pem_private_key(
            priv_file.read(),
            password=None,
            backend=default_backend()
        )

    # Расшифровка AES ключа с использованием RSA
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Расшифровка данных с использованием AES-GCM
    decryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Сохранение расшифрованного файла
    decrypted_file_path = encrypted_file_path[:-4]  # Убираем .enc
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

    return decrypted_file_path


def find_encrypted_files(directories):
    """Функция для поиска зашифрованных файлов в указанных директориях."""
    encrypted_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.enc'):
                    encrypted_files.append(os.path.join(root, file))
    return encrypted_files


def encrypt_file(public_key_path, file_path):
    """Шифрование файла с использованием RSA."""
    # Чтение данных из файла
    with open(file_path, 'rb') as f:
        plaintext = f.read()

    # Загрузка публичного ключа
    with open(public_key_path, 'rb') as pub_file:
        public_key = serialization.load_pem_public_key(pub_file.read(), backend=default_backend())

    # Шифрование данных с использованием RSA
    encrypted_data = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Сохранение зашифрованного файла
    encrypted_file_path = file_path + ".enc"
    with open(encrypted_file_path, 'wb') as f:
        f.write(encrypted_data)

    return encrypted_file_path

def decrypt_file(private_key_path, encrypted_file_path):
    """Расшифровка файла с использованием RSA."""
    # Чтение зашифрованного файла
    with open(encrypted_file_path, 'rb') as f:
        encrypted_data = f.read()

    # Чтение приватного ключа RSA
    with open(private_key_path, 'rb') as priv_file:
        private_key = serialization.load_pem_private_key(
            priv_file.read(),
            password=None,
            backend=default_backend()
        )

    # Расшифровка данных с использованием приватного ключа RSA
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Сохранение расшифрованного файла
    decrypted_file_path = encrypted_file_path[:-4]  # Убираем .enc
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

    return decrypted_file_path


# Основная функция
def main():
    json_file = "keys.json"
    
    # Проверяем, существует ли файл keys.json
    if not os.path.exists(json_file):
        with open(json_file, 'w') as file:
            json.dump([], file)  # Создаем пустой JSON файл

    while True:
        print_menu()
        choice = input("Выберите действие (0-13): ")

        if choice == "1":
            username = input("Введите имя пользователя: ")
            priv_filename, pub_filename = generate_key_pair(username)
            save_keys_to_json(username, pub_filename, priv_filename, json_file)

        elif choice == "2":
            # Запрос текста для шифрования
            print("Введите текст для шифрования:")
            text_to_encrypt = input()

            # Получение пользователя для шифрования
            public_key_path, _ = get_user_to_encrypt(json_file)
            if public_key_path:
                encrypted_message = encrypt_text(public_key_path, text_to_encrypt)
                print(f"Зашифрованный текст: {encrypted_message}")

        elif choice == "3":
            # Получение пользователя для расшифровки
            private_key_path, _ = get_user_to_decrypt(json_file)
            if private_key_path:
                encrypted_message = input("Введите зашифрованный текст: ")
                decrypted_message = decrypt_text(private_key_path, encrypted_message)
                if decrypted_message:
                    print(f"Расшифрованный текст: {decrypted_message}")

        elif choice == "4":
            # Получение текста от пользователя
            text_to_encrypt = get_multiline_input()

            # Получение пользователя для шифрования
            public_key_path, _ = get_user_to_encrypt(json_file)
            if public_key_path:
                encrypted_data = encrypt_text_gcm(public_key_path, text_to_encrypt)
                print(f"Зашифрованные данные (AES-GCM): {encrypted_data}")


        elif choice == "5":
            # Получение пользователя для расшифровки
            private_key_path, _ = get_user_to_decrypt(json_file)
            if private_key_path:
                encrypted_data_str = input("Введите зашифрованные данные (как словарь): ")
                encrypted_data = eval(encrypted_data_str)
                decrypted_text = decrypt_text_gcm(private_key_path, encrypted_data)
                if decrypted_text:
                    print(f"Расшифрованный текст: {decrypted_text}")

        elif choice == "6":
            # Получение пользователя для шифрования файла
            public_key_path, _ = get_user_to_encrypt(json_file)
            if public_key_path:
                file_to_encrypt = input("Введите путь к файлу для шифрования: ")
                encrypted_file_path = encrypt_file(public_key_path, file_to_encrypt)
                print(f"Файл зашифрован и сохранен как: {encrypted_file_path}")

        elif choice == "7":
            # Получение пользователя для расшифровки файла
            private_key_path, _ = get_user_to_decrypt(json_file)
            if private_key_path:
                directories = input("Введите пути к директориям для поиска зашифрованных файлов, разделенные запятой: ").split(',')
                encrypted_files = find_encrypted_files(directories)
                
                if not encrypted_files:
                    print("Зашифрованные файлы не найдены.")
                    continue

                print("Найденные зашифрованные файлы:")
                for idx, file in enumerate(encrypted_files):
                    print(f"{idx + 1}. {file}")

                file_choice = int(input("Выберите файл для расшифровки (введите номер): ")) - 1

                if file_choice < 0 or file_choice >= len(encrypted_files):
                    print("Неверный выбор.")
                    continue

                decrypted_file_path = decrypt_file(private_key_path, encrypted_files[file_choice])
                print(f"Файл расшифрован и сохранен как: {decrypted_file_path}")

        elif choice == "8":
            # Получение пользователя для шифрования файла с использованием AES-GCM
            public_key_path, _ = get_user_to_encrypt(json_file)
            if public_key_path:
                file_to_encrypt = input("Введите путь к файлу для шифрования: ")
                encrypted_file_path = encrypt_file_gcm(public_key_path, file_to_encrypt)
                print(f"Файл зашифрован (AES-GCM) и сохранен как: {encrypted_file_path}")

        elif choice == "9":
            # Получение пользователя для расшифровки файла с использованием AES-GCM
            private_key_path, _ = get_user_to_decrypt(json_file)
            if private_key_path:
                directories = input("Введите пути к директориям для поиска зашифрованных файлов, разделенные запятой: ").split(',')
                encrypted_files = find_encrypted_files(directories)
                
                if not encrypted_files:
                    print("Зашифрованные файлы не найдены.")
                    continue

                print("Найденные зашифрованные файлы (AES-GCM):")
                for idx, file in enumerate(encrypted_files):
                    print(f"{idx + 1}. {file}")

                file_choice = int(input("Выберите файл для расшифровки (введите номер): ")) - 1

                if file_choice < 0 or file_choice >= len(encrypted_files):
                    print("Неверный выбор.")
                    continue

                decrypted_file_path = decrypt_file_gcm(private_key_path, encrypted_files[file_choice])
                print(f"Файл расшифрован (AES-GCM) и сохранен как: {decrypted_file_path}")

        elif choice == "10":
            username = input("Введите имя пользователя, для которого добавляется публичный ключ друга: ")
            friend_pub_key_path = input("Введите путь к файлу с публичным ключом друга: ")
            add_friend_key(username, friend_pub_key_path, json_file)
        elif choice == "11":    
            with open(json_file, 'r') as file:
                data = json.load(file)
                print("Список пользователей:")
                for entry in data:
                    public_key = entry.get('public_key_path', 'Не указан')
                    private_key = entry.get('private_key_path', 'Не указан')
                    print(f"Имя пользователя: {entry['username']}, Путь к публичному ключу: {public_key}, Путь к приватному ключу: {private_key}")

        elif choice == "12":
            username = input("Введите имя пользователя для удаления из JSON файла: ")
            delete_user_from_json(username, json_file)
        elif choice == "13":    
            """ Сканирование директорий и добавление новых публичных ключей """
            key_type = input("Какой тип ключей вы хотите добавить? (public/private): ").strip().lower()
            if key_type not in ['public', 'private', '1', '2']:
                print("Неверный тип ключа. Укажите 'public' (1) или 'private' (2).")
                continue
            if key_type == '1':
                key_type = 'public'
            if key_type == '2': 
                key_type = 'private'
            found_keys = scan_for_keys(json_file, key_type)
            if not found_keys:
                print(f"Новые {key_type} ключи не найдены.")
            else:
                print(f"Найденные новые {key_type} ключи:")
                for idx, key_path in enumerate(found_keys):
                    print(f"{idx + 1}. {key_path}")

                # Запрос на добавление ключей
                for key_path in found_keys:
                    username = input(f"Введите имя пользователя для ключа {key_path}: ").strip()
                    
                    # Проверка, что имя пользователя введено
                    if not username:
                        print("Имя пользователя не может быть пустым. Ключ не будет добавлен.")
                        continue
                    
                    add_friend_key(username, key_path, key_type, json_file)
        elif choice == "14":
            info()
        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите от 0 до 13.")

if __name__ == "__main__":
    main()




"""АФИГЕТЬ 800 строк!!!"""
