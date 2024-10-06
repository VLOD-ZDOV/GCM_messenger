import socket
import threading
import json

clients = {}  # Словарь для хранения подключений клиентов по их имени
message_buffer = {}  # Буфер для хранения сообщений для клиентов, которые не в сети

# Функция для обработки сообщений от клиента
def handle_client(client_socket, client_address, client_name):
    print(f"{client_name} подключился с адреса {client_address}")
    clients[client_name] = client_socket  # Сохраняем сокет клиента в словарь

    # Проверяем, есть ли сообщения в буфере для клиента
    if client_name in message_buffer and message_buffer[client_name]:
        for msg in message_buffer[client_name]:
            client_socket.send(msg.encode())  # Отправляем непрочитанные сообщения
        message_buffer[client_name] = []  # Очищаем буфер

    try:
        while True:
            message = client_socket.recv(4096).decode()  # Ожидаем сообщение от клиента

            if not message:
                break

            # Преобразуем сообщение обратно в словарь
            data = json.loads(message)
            recipient_name = data['recipient']
            encrypted_message = json.dumps(data['encrypted_message'])  # Преобразуем обратно в строку для отправки

            # Проверяем, есть ли получатель в сети
            if recipient_name in clients:
                # Отправляем сообщение получателю
                clients[recipient_name].send(f"{client_name}: {encrypted_message}".encode())
            else:
                # Если получатель не в сети, сохраняем сообщение в буфер
                if recipient_name not in message_buffer:
                    message_buffer[recipient_name] = []
                message_buffer[recipient_name].append(f"{client_name}: {encrypted_message}")

    except ConnectionResetError:
        print(f"{client_name} отключился")
    
    finally:
        client_socket.close()
        del clients[client_name]

# Запуск сервера
def start_server():
    host = '0.0.0.0'
    port = 12378
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Сервер запущен и ожидает подключений...")

    while True:
        client_socket, client_address = server_socket.accept()
        client_name = client_socket.recv(1024).decode()  # Получаем имя клиента
        threading.Thread(target=handle_client, args=(client_socket, client_address, client_name)).start()

if __name__ == '__main__':
    start_server()
