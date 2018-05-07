import socket
TCP_PORT = 5005

def my_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return  s.getsockname()[0]


def get_range():
    ip=my_ip_address().split(".")
    base_ip=u".".join(ip[:3])+'.0/24'
    return base_ip


def send_message(ip, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, TCP_PORT))
    s.send(message)
    s.settimeout(5)
    data = s.recv(2048)
    s.close()
    return data