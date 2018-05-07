#! /usr/bin/env python

import threading
import socket
import time
import datetime

tcp_port = 5005
b_size = 2048  # Normally 2048, but we want fast response


#   return my ip address
def my_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    return my_ip


# receive data from slave function - run for each slave as a thread function
def receive_data_slave(devices):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((my_ip_address(), tcp_port))
    s.listen(10)
    while True:
        print "not listening"
        try:
            conn, addr = s.accept()
            data = conn.recv(b_size)
            if not data:
                break
            else:
                print "received data from:%s data is:%s " % (addr[0], data)
                # TODO check if data is type1:request name or type2: get data
                conn.send("Master: Thanks got INFO at:"+str(datetime.datetime.now()))  # echo
        except:
            conn.close()
    conn.close()
    return



def main(devices):
    receive_data_slave(devices)
