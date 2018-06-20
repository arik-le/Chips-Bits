import socket
import subprocess
import threading
import pickle
import os
import time
from message import Message
import message as mess
from gVariable import *



def my_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return  s.getsockname()[0]


def get_range():
    ip=my_ip_address().split(".")
    base_ip=u".".join(ip[:3])+'.0/24'
    return base_ip


def get_name_from_ip(ip,devices):
    for device in devices:
        if ip == device.ip:
            return device.name
    return None


def send_message(message):
    # res = None
    # message_obj = [message.type, message.body]
    data_to_send = pickle.dumps(message)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((message.device.ip, TCP_PORT))
        s.send(data_to_send)
        s.settimeout(5)
        data = s.recv(2048)
        s.close()
        res = data
    except:
        res = None

    return res


def file_exist(file_name):
    return os.path.isfile(file_name)


def send_messages(devices):
    while open("master alive", 'r').read() == "T":
        res = None
        if mess.exist():
            message_to_send = mess.get()
            message_to_send.update_master(devices[0])
            for i in range(3):
                print "Try to send..."
                res = send_message(message_to_send)
                if res is not None:
                    mess.remove_from_queue()
                    print "Message arrived"
                    break
                # time.sleep(3)
            print res
            if res is None:
                print "Message not arrived"
                open("master alive", 'w').write("F")


# Configure subprocess to hide the console window
def check_is_alive(devices):
    info = None
    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
    print "Trying to PING Master"
    output = subprocess.Popen(['ping', '-c', '2', '-w', '1', str(devices[0].ip)], stdout=subprocess.PIPE,
                              startupinfo=info).communicate()[0]
    
    if " 0 packets received, 100% packet loss" in output.decode('utf-8'):
        #host is not active any more
        threads = []

        massage = ["3", "Master is Dead"]
        for i in range(1, len(devices)-1):
            if my_ip_address() != devices[i].ip:
                t = threading.Thread(target=send_message(), args=(devices[i].ip, massage))
                threads.append(t)
                t.start()
        for t in threads:
            t.join()

        devices.pop(0)
        devices[0].master = True
        for d in devices:
            print d
        if devices[0].ip == my_ip_address():
            return True
        return False
    else:
        print "Master is Alive and Busy"
        return False
