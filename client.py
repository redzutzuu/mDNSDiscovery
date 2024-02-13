import socket
import tkinter as tk
import time
from datetime import datetime


def configure_resources(resources, response_listbox, status_label, ttl=60):
    multicast_group = '224.0.0.251'
    server_port = 8081

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        for resource in resources:
            status_label.config(text=f"Trimitere solicitare pentru {resource}...")
            response_listbox.update_idletasks()

            client_socket.sendto(resource.encode(), (multicast_group, server_port))
            time.sleep(0.1)

            data, source_address = client_socket.recvfrom(1024)
            cleaned_response = data.decode('latin-1').split('Value=')[1].strip()
            cleaned_response = cleaned_response.replace('\x00', '').replace('<', '')

            hostname = cleaned_response.split('-')[-1].split(' de la')[0].replace('%', '').strip()

            source_ip, source_port = source_address

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            response_text = f"{timestamp} - Raspuns pentru {resource}: {cleaned_response} cu adresa IP {source_ip}:{source_port}"

            response_listbox.insert(tk.END, response_text)
            status_label.config(text="Configurare trimisa!")

            response_listbox.after(5000, lambda: status_label.config(text=""))

    except Exception as e:
        print(f"Configurare esuata: {e}")
    finally:
        client_socket.close()

def export_to_file(response_listbox):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"resource_data_{timestamp}.txt"
    with open(filename, 'w') as file:
        for item in response_listbox.get(0, tk.END):
            file.write(item + '\n')
    print(f"Datele au fost exportate în fisierul: {filename}")


def start_monitoring():
    def on_submit():
        selected = []
        if cpu_var.get():
            selected.append("CPU")
        if memory_var.get():
            selected.append("Memory")
        if disk_var.get():
            selected.append("Disk")
        if network_var.get():
            selected.append("Network")
        if cpu_temp_var.get():
            selected.append("CPU Temperature")

        try:
            ttl_value = int(ttl_entry.get())
        except ValueError:
            status_label.config(text="Valoare TTL invalidă. Utilizați un număr întreg.")
            return

        if selected:
            configure_resources(selected, response_listbox, status_label, ttl=ttl_value)
        else:
            status_label.config(text="Selectati cel putin o resursa!")

    root = tk.Tk()
    root.title("Configurator Monitorizare")

    cpu_var = tk.BooleanVar()
    memory_var = tk.BooleanVar()
    disk_var = tk.BooleanVar()
    network_var = tk.BooleanVar()
    cpu_temp_var = tk.BooleanVar()

    cpu_check = tk.Checkbutton(root, text="CPU", variable=cpu_var)
    memory_check = tk.Checkbutton(root, text="Memory", variable=memory_var)
    disk_check = tk.Checkbutton(root, text="Disk", variable=disk_var)
    network_check = tk.Checkbutton(root, text="Network", variable=network_var)
    cpu_temp_check = tk.Checkbutton(root, text="CPU Temperature", variable=cpu_temp_var)

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    export_button = tk.Button(root, text="Export to File", command=lambda: export_to_file(response_listbox))
    status_label = tk.Label(root, text="")

    ttl_label = tk.Label(root, text="TTL:")
    ttl_entry = tk.Entry(root)
    ttl_label.pack()
    ttl_entry.pack()

    response_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=200, height=10)
    response_listbox.pack()

    cpu_check.pack()
    memory_check.pack()
    disk_check.pack()
    network_check.pack()
    cpu_temp_check.pack()
    submit_button.pack()
    export_button.pack()
    status_label.pack()

    root.mainloop()

if __name__ == "__main__":
    start_monitoring()
