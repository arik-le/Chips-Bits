import socket
import subprocess
import threading
import pickle
import os
import datetime
import time
from message import Message
import message as mess
from constant_variable import *

# return my ip address
def my_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return  s.getsockname()[0]

# get range of ip addresses
def get_range():
    ip=my_ip_address().split(".")
    base_ip=u".".join(ip[:3])+'.0/24'
    return base_ip

# get devices host name
def get_name_from_ip(ip,devices):
    for device in devices:
        if ip == device.ip:
            return device.name
    return None


# send message function
def send_message(message):
    data_to_send = pickle.dumps(message)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(5)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((message.device.ip, TCP_PORT))
        s.send(data_to_send)
        data = s.recv(2048)
        s.close()
        res = data
    except:
        res = None
    return res

# return the path of the file
def file_exist(file_name):
    return os.path.isfile(file_name)


# send several messages
def send_messages(devices):
    while open("master alive", 'r').read() == "T":
        res = None
        if mess.exist():
            message_to_send = mess.get()
            message_to_send.update_master(devices[0])
            for i in range(1):
                print "Try to send..."
                res = send_message(message_to_send)
                if res is not None:
                    mess.remove_from_queue()
                    print "Message arrived"
                    break
            if res is None:
                print "Message not arrived"
                open("master alive", 'w').write("F")


# add message or sample to log file
def add_to_log_file(message):
    open(TRANSFER_FILE, "a").write(message.body + "\n")


# return the actual time for proper package of data
def get_time():
    now = datetime.datetime.now()
    minute = now.minute
    minute_str = ""
    if minute < 10:
        minute_str += "0"
    minute_str += str(minute)
    return str(now.hour) + ":" + minute_str + ":" + str(now.second)


# return average val between ranges s to f
def get_average(samples, s, f):
    total = 0.0
    for i in range(s, f):
        total += samples[i].range
    return total / (f - s)