import socket
import threading
from tkinter import *
from tkinter import scrolledtext, simpledialog, messagebox

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            display.config(state=NORMAL)
            display.insert(END, message)
            display.yview(END)
            display.config(state=DISABLED)
        except ConnectionAbortedError:
            break
        except Exception as e:
            print("An error occurred.")
            client.close()
            break

def send(event=None): 
    try:
        if  my_name == "":
            message = f"Unknown: {message_entry.get()}"
        else:
            message = f"{my_name}: {message_entry.get()}"
        if message_entry.get():
            client.send(message.encode('utf-8'))

        message_entry.delete(0, END)
    except Exception as e:
        print(f"Error sending message: {str(e)}")

def on_closing(event=None):
    message_entry.delete(0, END)
    window.destroy()

def connect_to_server():
    global client, my_name
    if not ip_entry.get() or not port_entry.get().isdigit():
        messagebox.showerror("錯誤", "請輸入有效的IP地址和端口。")
        ip_entry.delete(0, END)
        port_entry.delete(0, END)
        return
    host = ip_entry.get()
    port = int(port_entry.get())
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        display.config(state=NORMAL)
        display.insert(END, "[You join the room]\n")
        display.yview(END)
        display.config(state=DISABLED)
        my_name = simpledialog.askstring("Name:", "PROFILE NAME\n (type nothing to be anonymous)", parent=window)
        window.geometry("500x400+100+100")
        
        join_button.destroy()
        leave_button = Button(window, text="Leave Room", command=on_closing, font=("Arial", 10), bg="red", fg="black")
        leave_button.grid(row=2, column=2, columnspan=2, pady=5)
        chat_label.grid(row=3, column=0, sticky=W)
        
        you_label = Label(window, text="YOU:", font=("Times New Roman", 14, "italic"), bg="pink")
        you_label.grid(row=4, column=0, padx=(0, 5), pady=5, sticky=W)
        display.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="e")
        send_button.grid(row=4, column=2, padx=(0, 5), pady=5, sticky=W)
        message_entry.grid(row=4, column=1, padx=(0, 5), pady=5, sticky=W)

        threading.Thread(target=receive, daemon=True).start()
    except Exception as e:
        messagebox.showerror("連接錯誤", f"無法連接到 {host}:{port}\n錯誤訊息: {str(e)}")
        print(f"Cannot connect to: {host}:{port}")

window = Tk()
window.title("Room:『PinkyPinkyPinky3種口味』")
window.geometry("300x100+100+100")
window.configure(bg="pink")

l_style = ("Times New Roman", 14)
big_style = ("Times New Roman", 14, "bold", "italic")

Label(window, text="IP:", font=l_style, bg="pink").grid(row=0, column=0, sticky=W)
ip_entry = Entry(window)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

Label(window, text="PORT:", font=l_style, bg="pink").grid(row=1, column=0, sticky=W)
port_entry = Entry(window)
port_entry.grid(row=1, column=1, padx=5, pady=5)

chat_label = Label(window, text="C\nH\nA\nT", font=big_style, bg="pink")

join_button = Button(window, text="JOIN", command=connect_to_server, font=("Arial", 12), bg="#4CAF50", fg="white")
join_button.grid(row=2, column=0, columnspan=2, pady=5)

display = scrolledtext.ScrolledText(window, state=DISABLED, height=15, width=50)
message_entry = Entry(window, width=40)
message_entry.bind("<Return>", send)
send_button = Button(window, text="Send", command=send, font=("Arial", 10), bg="orange", fg="white")

window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()
