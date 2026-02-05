import socket
import threading
import tkinter as tk
from tkinter import messagebox
from pynput.mouse import Button, Controller
import sys

# --- KONFIGURASI ---
PORT = 12345

class TargetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetCursor Target")
        self.root.geometry("300x300")
        self.root.resizable(False, False)

        # Mengambil IP Address Lokal secara otomatis
        self.my_ip = socket.gethostbyname(socket.gethostname())

        # --- Elemen UI ---
        tk.Label(root, text="Target Monitor", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(root, text="IP Address Anda:", font=("Arial", 10)).pack()
        self.lbl_ip = tk.Label(root, text=self.my_ip, font=("Arial", 16, "bold"), fg="blue")
        self.lbl_ip.pack(pady=5)
        
        tk.Label(root, text="Status:", font=("Arial", 10)).pack()
        self.lbl_status = tk.Label(root, text="Menunggu Koneksi...", font=("Arial", 10, "italic"), fg="orange")
        self.lbl_status.pack(pady=5)

        self.btn_stop = tk.Button(root, 
                                  text="MATIKAN SERVER", 
                                  command=self.stop_server, 
                                  bg="red", 
                                  fg="white",
                                  font=("Arial", 12, "bold"), 
                                  padx=20, pady=10,           
                                  cursor="hand2")
        self.btn_stop.pack(pady=15)

        # Flag untuk loop server
        self.running = True
        self.server_socket = None

        # Jalankan server di thread terpisah agar UI tidak macet
        self.thread = threading.Thread(target=self.start_server_logic)
        self.thread.daemon = True # Agar thread mati saat aplikasi ditutup
        self.thread.start()

    def update_status(self, text, color):
        # Fungsi aman untuk update UI dari thread lain
        self.lbl_status.config(text=text, fg=color)

    def start_server_logic(self):
        mouse = Controller()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind(('0.0.0.0', PORT))
            self.server_socket.listen(1)
            
            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    self.update_status(f"Terhubung: {addr[0]}", "green")
                    
                    while self.running:
                        data = conn.recv(1024).decode('utf-8')
                        if not data:
                            break
                        
                        # Logika Mouse
                        try:
                            if "click" in data:
                                mouse.click(Button.left, 1)
                            else:
                                parts = data.split(',')
                                if len(parts) == 2:
                                    x, y = int(parts[0]), int(parts[1])
                                    mouse.position = (x, y)
                        except ValueError:
                            pass
                    
                    conn.close()
                    self.update_status("Menunggu Koneksi...", "orange")
                    
                except OSError:
                    break # Keluar loop jika socket ditutup manual

        except Exception as e:
            if self.running:
                self.update_status(f"Error: {e}", "red")

    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = TargetApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_server) # Handle tombol X pojok kanan atas
    root.mainloop()