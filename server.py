import socket
import psutil
import struct
import tkinter as tk

def build_dns_sd_packet(service_name, response, ttl=60, hostname=""):
    txt_record = f"Value={response}".encode('utf-8')
    srv_record = struct.pack('!HHI', 0, 0, 8081)  # SRV record: Priority=0, Weight=0, Port=8081
    a_record = socket.inet_aton('127.0.0.1')  # A record: IPv4 address (127.0.0.1)

    dns_sd_packet = (
        b'\x00\x00'  # ID
        b'\x81\x80'  # Flags
        b'\x00\x01'  # Questions
        b'\x00\x03'  # Answer RRs (3 records)
        b'\x00\x00'  # Authority RRs
        b'\x00\x00'  # Additional RRs
        + service_name.encode() + b'\x00'  # Service name
        + b'\x00\x0c\x00\x01'  # Type: PTR record
        + b'\x00\x00\x00\x3c'  # Class: IN
        + struct.pack('!I', 60)  # TTL: 60 seconds
        + struct.pack('!H', len(service_name.encode()) + 1)  # Length of service name
        + service_name.encode() + b'\x00'  # Service name
        + srv_record  # SRV record
        + a_record  # A record
        + struct.pack('!H', len(txt_record) + 1)  # Length of txt_record
        + txt_record  # TXT record
        + struct.pack('!I', ttl)  # TTL
        + hostname.encode() + b'\x00'  # Hostname
    )
    return dns_sd_packet

def get_cpu_percent():
    return str(psutil.cpu_percent(interval=1))

def get_memory_percent():
    memory = psutil.virtual_memory()
    return str(memory.percent)

def get_disk_percent():
    disk = psutil.disk_usage('/')
    return str(disk.percent)

def get_network_percent():
    network = psutil.net_io_counters()
    return str(network)

def get_cpu_temperature():
    temp = psutil.sensors_temperatures()
    cpu_temp = temp['coretemp'][0].current
    return str(cpu_temp)

def start_server():
    def update_hostname():
        hostname = hostname_var.get()
        return f"Hostname: {hostname}" if hostname else "Hostname not set"

    def on_button_click():
        status_label.config(text=update_hostname())

    root = tk.Tk()
    root.title("Server GUI")

    hostname_var = tk.StringVar()
    hostname_entry = tk.Entry(root, textvariable=hostname_var, width=30)
    set_hostname_button = tk.Button(root, text="Set Hostname", command=on_button_click)
    status_label = tk.Label(root, text=update_hostname())

    hostname_entry.pack()
    set_hostname_button.pack()
    status_label.pack()

    print("Serverul asculta pe adresa de multicast 224.0.0.251, portul 8081...")

    multicast_group = '224.0.0.251'
    server_port = 8081

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', server_port))

    while True:
        data, address = server_socket.recvfrom(1024)
        request = data.decode()

        response = ''

        if request == 'CPU':
            response = get_cpu_percent() + '% - de la hostname '
        elif request == 'Memory':
            response = get_memory_percent() + '% - de la hostname '
        elif request == 'Disk':
            response = get_disk_percent() + '% - de la hostname '
        elif request == 'Network':
            response = get_network_percent() + ' - de la hostname '
        elif request == 'CPU Temperature':
            response = get_cpu_temperature() + '°C - de la hostname '

        dns_sd_packet = build_dns_sd_packet("MyService", response, hostname=socket.gethostname())
        server_socket.sendto(dns_sd_packet, address)

if __name__ == "__main__":
    start_server()
