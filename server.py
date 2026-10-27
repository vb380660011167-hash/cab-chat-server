import socket
import threading
import os

# Список клієнтів та їхніх нікнеймів
clients = {}
nicknames = {}

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                remove_client(client)

def broadcast_user_list():
    user_list_str = "USERLIST:" + ",".join(nicknames.values())
    for client in clients:
        try:
            client.send(user_list_str.encode('utf-8'))
        except:
            pass

def handle_client(client_sock):
    try:
        # Отримуємо нікнейм першим повідомленням
        nickname = client_sock.recv(1024).decode('utf-8').strip()
        if not nickname:
            nickname = "Anonym"
        
        clients[client_sock] = client_sock.getpeername()
        nicknames[client_sock] = nickname

        print(f"[+] {nickname} підключився.")
        broadcast(f"SYSTEM:{nickname} приєднався до чату.".encode('utf-8'), client_sock)
        broadcast_user_list()

        while True:
            msg = client_sock.recv(1024)
            if not msg:
                break
            message_text = msg.decode('utf-8')
            print(f"[{nickname}]: {message_text}")
            # Пересилаємо у форматі "Нік: Повідомлення"
            full_msg = f"{nickname}: {message_text}".encode('utf-8')
            broadcast(full_msg)

    except Exception as e:
        print(f"[-] Помилка з клієнтом: {e}")
    finally:
        remove_client(client_sock)

def remove_client(client_sock):
    if client_sock in clients:
        nickname = nicknames.get(client_sock, "Хтось")
        print(f"[-] {nickname} відключився.")
        
        del clients[client_sock]
        if client_sock in nicknames:
            del nicknames[client_sock]
            
        client_sock.close()
        broadcast(f"SYSTEM:{nickname} покинув чат.".encode('utf-8'))
        broadcast_user_list()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Хмарні хостинги передають порт через змінні середовища, за замовчуванні беремо 9090
    port = int(os.environ.get("PORT", 9090))
    
    # Слухаємо на всіх інтерфейсах (0.0.0.0)
    server.bind(("0.0.0.0", port))
    server.listen()
    print(f"[*] Сервер Cab запущено на порті {port}...")

    while True:
        client_sock, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_sock,), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()