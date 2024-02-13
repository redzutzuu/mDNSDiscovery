import socket
import tkinter as tk
from datetime import datetime

service_cache = {}

def discover_services(response_listbox, status_label):
    global service_cache
    multicast_group = '224.0.0.251'
    server_port = 8081

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(2)

    try:
        status_label.config(text="Descoperire servicii în curs...")
        response_listbox.update_idletasks()

        client_socket.sendto("Discover".encode(), (multicast_group, server_port))

        while True:
            try:
                data, source_address = client_socket.recvfrom(1024)
                cleaned_response = data.decode('latin-1').split('Value=')[1].strip()

                source_ip, source_port = source_address

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                response_listbox.insert(tk.END, f"{timestamp} - Serviciu disponibil la {source_ip}:{source_port}: {cleaned_response}")
                response_listbox.update_idletasks()

                service_cache[source_ip] = cleaned_response

            except socket.timeout:
                break

    except Exception as e:
        print(f"Descoperire servicii esuata: {e}")
    finally:
        client_socket.close()

def on_service_select(event, response_listbox, status_label):
    global service_cache
    selected_index = response_listbox.curselection()

    if selected_index:
        selected_item = response_listbox.get(selected_index[0])
        status_label.config(text=f"Selected: {selected_item}")

        parts = selected_item.split('-')
        if len(parts) >= 2:
            last_part = parts[-1].strip()
            source_ip = last_part.split(':')[0].strip()

            if source_ip in service_cache:
                value = service_cache[source_ip]
                print(f"Valoare resursa (din cache): {value}")
            else:
                print("Valoare resursa nu este in cache. Efectuati o descoperire pentru a o adauga.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Descoperire Servicii")

    response_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=200, height=10)
    response_listbox.pack()

    discover_button = tk.Button(root, text="Discover Services", command=lambda: discover_services(response_listbox, status_label))
    discover_button.pack()

    response_listbox.bind('<ButtonRelease-1>', lambda event: on_service_select(event, response_listbox, status_label))

    status_label = tk.Label(root, text="")
    status_label.pack()

    root.mainloop()
