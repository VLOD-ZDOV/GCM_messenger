import socket
import threading
import json
from SCmess import encrypt_text_gcm, get_user_to_encrypt  # Импортируем функции шифрования и выбора пользователя
from SCmess import decrypt_text_gcm, get_user_to_decrypt  # Импортируем функции для дешифровки
import sys

# Функция для выбора ключа
def select_private_key():
    private_key_path, user = get_user_to_decrypt('keys.json')
    if private_key_path:
        print("У вас новый зашифрованный ключ, выбирается автоматически.")
        return private_key_path
    else:
        print("Не удалось найти ключ для расшифровки.")
        return None

# Функция для прослушивания сообщений от сервера и попытки их расшифровки
def listen_for_messages(client_socket, client_name):
    print("Прослушивание чата началось... (нажмите Ctrl+c для завершения прослушивания)")
    try:
        while True:
            message = client_socket.recv(4096).decode()  # Получаем сообщение с сервера
            if not message:
                break

            sender_name, encrypted_data = message.split(': ', 1)

            print("У вас новое сообщение")

            # Получаем все доступные ключи для расшифровки
            private_key_path, user = get_user_to_decrypt('keys.json')

            if not private_key_path:
                print("Не удалось найти ключ для расшифровки.")
                continue

            # Если есть один ключ, расшифровываем им автоматически
            if isinstance(private_key_path, str):
                print(f"Расшифровывается с помощью ключа {user['username']}")
                try:
                    encrypted_data = json.loads(encrypted_data)  # Преобразуем строку обратно в словарь
                    decrypted_message = decrypt_text_gcm(private_key_path, encrypted_data)  # Дешифруем сообщение
                    print(f"{sender_name} -> {client_name}: {decrypted_message}")
                except Exception as e:
                    print(f"Не удалось расшифровать сообщение - {str(e)}")

            # Если несколько ключей, предложить выбрать
            elif isinstance(private_key_path, list):
                print("Выберите ключ для расшифровки:")
                for idx, key_info in enumerate(private_key_path, 1):
                    print(f"{idx}. {key_info['username']}")

                key_choice = int(input("Введите номер ключа: ")) - 1
                selected_key = private_key_path[key_choice]['private_key_path']

                try:
                    encrypted_data = json.loads(encrypted_data)  # Преобразуем строку обратно в словарь
                    decrypted_message = decrypt_text_gcm(selected_key, encrypted_data)  # Дешифруем сообщение
                    print(f"{sender_name} -> {client_name}: {decrypted_message}")
                except Exception as e:
                    print(f"Не удалось расшифровать сообщение - {str(e)}")
    except (EOFError, KeyboardInterrupt):
        print("\nЗавершение прослушивания чата...")
        return

# Функция для отправки сообщений на сервер
def send_message(client_socket):
    print("Отправка сообщения началась...")
    while True:
        try:
            # Получаем многострочный ввод от пользователя через SCmess.py
            print("Введите ваше сообщение (нажмите Ctrl+D для завершения ввода):")
            message = sys.stdin.read()  # Получаем многострочный ввод сообщения

            if not message.strip():
                print("Сообщение пустое, повторите ввод.")
                continue

            # Получаем публичный ключ получателя (логика уже есть в SCmess.py)
            public_key_path, recipient = get_user_to_encrypt('keys.json')  # Используем выбор пользователя из программы
            if public_key_path:
                encrypted_message = encrypt_text_gcm(public_key_path, message)  # Шифруем сообщение

                # Форматируем зашифрованное сообщение для отправки на сервер
                message_to_send = json.dumps({
                    'recipient': recipient['username'],
                    'encrypted_message': encrypted_message
                })

                client_socket.send(message_to_send.encode())  # Отправляем зашифрованное сообщение на сервер
                print(f"Сообщение отправлено пользователю {recipient['username']}.")
                break
        except (EOFError, KeyboardInterrupt):
            print("\nОтмена ввода сообщения.")
            break

# Основное меню
def menu(client_socket, client_name):
    while True:
        print("\nМеню:")
        print("1. Прослушивать чат")
        print("2. Отправить сообщение")
        print("0. Выйти")
        choice = input("Выберите действие (1, 2, 0): ")

        if choice == "1":
            # Запускаем прослушивание чата
            listen_for_messages(client_socket, client_name)
        elif choice == "2":
            # Отправляем сообщение
            send_message(client_socket)
        elif choice == "0":
            print("Завершение программы...")
            client_socket.close()
            break
        else:
            print("Неверный выбор, попробуйте снова.")

# Функция клиента
def client_program():
    client_name = input("Введите ваше имя: ")

    host = '192.168.X.X'  # IP сервера
    port = 12378  # Порт сервера

    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Отправляем серверу имя клиента
    client_socket.send(client_name.encode())

    # Открываем основное меню
    menu(client_socket, client_name)

if __name__ == '__main__':
    client_program()
