from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
import socket
import threading
from queue import Queue
from PIL import Image, ImageTk

message_queue = Queue()
clients = []
server_running = True

def client_handler(conn, addr):
    with conn:
        message_queue.put(f"{addr} 已連接。\n")
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                message = f"{addr}: {data.decode('utf-8')}\n"
                message2 = f"{data.decode('utf-8')}\n"
                broadcast(message2)
                message_queue.put(message)
            except ConnectionResetError:
                break
        message_queue.put(f"{addr} 已斷開連接。\n")

badwords = ["幹", "去死", "你媽死了","車力巨人"]

def broadcast(message):
    if any(badword in message for badword in badwords):
        message = "Someone say the BAD WORDS!!!\n"
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            pass

def update_display():
    while not message_queue.empty():
        message = message_queue.get()
        display.insert(END, message)
        display.yview(END)
    window.after(100, update_display)

def run_server():
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        
        host = ip_entry.get()
        port = int(port_entry.get())
        server.bind((host, port))
        server.listen()
        message_queue.put("伺服器已啟動。等待連接...\n")
        start_button.destroy()
        while server_running:
            client_conn, client_addr = server.accept()
            clients.append(client_conn)
            threading.Thread(target=client_handler, args=(client_conn, client_addr), daemon=True).start()
    finally:
        server.close()

def start_server():
    global server_thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    update_display()

def stop_server():
    global server_running
    for client in clients:
        try:
            client.send("Server's Quit".encode('utf-8'))
            client.close()
        except Exception as e:
            print(f"Error sending message to a client: {str(e)}")
    server_running = False
    message_queue.put("伺服器已停止。\n")
    window.quit()

window = Tk()
window.title("Pinky Chat Server")
window.geometry("500x500+100+100")
window.resizable(True, True)
window.option_add("*TButton*font", ("Helvetica", 12))
window.option_add("*TButton*foreground", "white")
window.configure(bg="pink")

l_style = ("Times New Roman", 14)

Label(window, text="IP:", font=l_style, bg="pink").grid(row=0, column=1, sticky=W, pady=5)
ip_entry = Entry(window, font=("Helvetica", 12))
ip_entry.grid(row=0, column=2, pady=5)

Label(window, text="PORT:", font=l_style, bg="pink").grid(row=1, column=1, sticky=W, pady=5)
port_entry = Entry(window, font=("Helvetica", 12))
port_entry.grid(row=1, column=2, pady=5)

start_button = Button(window, text="啟動伺服器", command=start_server, font=("Helvetica", 12), bg="#4CAF50", fg="white")
start_button.grid(row=2, column=1, pady=10)

stop_button = Button(window, text="停止伺服器", command=stop_server, font=("Helvetica", 12), bg="#F44336", fg="white")
stop_button.grid(row=2, column=2, pady=10)

display = scrolledtext.ScrolledText(window, height=20, width=50, font=("Helvetica", 12), wrap=WORD)
display.configure(bg="white")
display.grid(row=3, column=1, columnspan=2, pady=10)

update_display()
window.mainloop()
