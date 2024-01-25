# server.py
import socket
import threading
from tkinter import *
from tkinter import scrolledtext
from queue import Queue

# 創建消息佇列
message_queue = Queue()
clients = []
server_running = True

# 伺服器端處理客戶端連接的函數
def client_handler(conn, addr):
    with conn:
        message_queue.put(f"{addr} 已連接。\n")
        while True:
            try:
                # 接收數據
                data = conn.recv(1024)
                if not data:
                    break
                # 廣播消息給所有客戶端
                message = f"{addr}: {data.decode('utf-8')}\n"
                message2 = f"{data.decode('utf-8')}\n"
                broadcast(message2, conn)
                message_queue.put(message)
            except ConnectionResetError:
                break
        message_queue.put(f"{addr} 已斷開連接。\n")

# 廣播給所有客戶端除了發送者
def broadcast(message, connection):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except: #捕捉所有異常
            client.close()
            if client in clients:
                clients.remove(client)

# 更新GUI的函數，從佇列中獲取消息
def update_display():
    while not message_queue.empty():
        message = message_queue.get()
        display.insert(END, message)
        display.yview(END)
    window.after(100, update_display)

# 啟動伺服器，接受連接
def run_server():
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # host = ip_entry.get()
        # port = int(port_entry.get())
        if not ip_entry.get() and not port_entry.get():
            host = "127.0.0.1"
            port = 20001
        else :
            host = ip_entry.get()
            port = int(port_entry.get())
        server.bind((host, port))
        server.listen()
        message_queue.put("伺服器已啟動。等待連接...\n")

        while server_running:
            client_conn, client_addr = server.accept()
            clients.append(client_conn)
            threading.Thread(target=client_handler, args=(client_conn, client_addr), daemon=True).start()
    finally:
        server.close()

# 開始伺服器線程
def start_server():
    global server_thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    update_display()

# 停止伺服器
def stop_server():
    global server_running
    server_running = False
    for client in clients:
        client.close()
    message_queue.put("伺服器已停止。\n")
    window.quit()

# 創建伺服器端的GUI
window = Tk()
window.title("聊天室伺服器")

# 輸入IP地址的標籤和輸入框
Label(window, text="IP 地址:").grid(row=0, column=0, sticky=W)
ip_entry = Entry(window)
ip_entry.grid(row=0, column=1)

# 輸入端口的標籤和輸入框
Label(window, text="端口:").grid(row=1, column=0, sticky=W)
port_entry = Entry(window)
port_entry.grid(row=1, column=1)

# 開始和停止伺服器的按鈕
start_button = Button(window, text="啟動伺服器", command=start_server)
start_button.grid(row=2, column=0, pady=5)

stop_button = Button(window, text="停止伺服器", command=stop_server)
stop_button.grid(row=2, column=1, pady=5)

# 滾動文本框顯示消息
display = scrolledtext.ScrolledText(window, height=20, width=50)
display.grid(row=3, column=0, columnspan=2)

# 在啟動GUI事件循環前調用update_display
update_display()
window.mainloop()
