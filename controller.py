import socket
import threading
import time
import tkinter as tk
from tkinter import messagebox
from pynput import mouse
import sys

PORT = 12345

class ControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetCursor Controller")
        self.root.geometry("350x200")
        
        # --- Elemen UI ---
        tk.Label(root, text="Controller Setup", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(root, text="Masukkan IP Target:", font=("Arial", 10)).pack()
        
        self.entry_ip = tk.Entry(root, font=("Arial", 12), justify='center')
        self.entry_ip.pack(pady=5)
        
        self.btn_connect = tk.Button(root, text="HUBUNGKAN", command=self.connect_to_target, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.btn_connect.pack(pady=10)
        
        self.lbl_info = tk.Label(root, text="Siap menghubungkan...", fg="gray")
        self.lbl_info.pack(pady=5)

        self.client_socket = None
        self.is_connected = False
        self.last_time = 0

    def connect_to_target(self):
        target_ip = self.entry_ip.get()
        self.lbl_info.config(text=f"Mencoba connect ke {target_ip}...", fg="orange")
        self.root.update()

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(3) # Timeout 3 detik jika IP salah
            self.client_socket.connect((target_ip, PORT))
            
            # Jika berhasil
            self.is_connected = True
            self.lbl_info.config(text="Terhubung! Gerakkan mouse Anda.", fg="green")
            self.btn_connect.config(state="disabled", text="Connected")
            self.entry_ip.config(state="disabled")
            
            # Mulai thread listener mouse
            threading.Thread(target=self.start_mouse_listener, daemon=True).start()
            
            messagebox.showinfo("Sukses", "Terhubung! Mouse gerakan Anda akan dikirim ke target.\nTutup aplikasi ini untuk berhenti.")

        except Exception as e:
            self.lbl_info.config(text="Gagal terhubung.", fg="red")
            messagebox.showerror("Error", f"Gagal konek ke {target_ip}.\nPastikan Target sudah jalan & IP benar.")

    def send_data(self, data):
        if self.is_connected:
            try:
                self.client_socket.send(data.encode('utf-8'))
            except:
                self.is_connected = False
                self.lbl_info.config(text="Koneksi terputus!", fg="red")

    def on_move(self, x, y):
        current_time = time.time()
        # Throttling 0.05 detik
        if current_time - self.last_time > 0.05:
            self.send_data(f"{x},{y}")
            self.last_time = current_time

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            self.send_data("click")

    def start_mouse_listener(self):
        # Listener pynput berjalan blocking, jadi harus di thread/fungsi terpisah
        with mouse.Listener(on_move=self.on_move, on_click=self.on_click) as listener:
            listener.join()

    def on_close(self):
        self.is_connected = False
        if self.client_socket:
            self.client_socket.close()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControllerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()