#! /usr/bin/env python

import threading
import socket
import time

tcp_port = 5005
b_size = 2048  # Normally 2048, but we want fast response


#   return my ip address
def my_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    return my_ip


# receive data from slave function - run for each slave as a thread function
def receive_data_slave(i,devices):
    ip = devices[i].ip
    name = devices[i].name
    #try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((my_ip_address(), tcp_port))
    s.listen(1)
    print "listen to:"+ip
    while True:
        print "not listening"
        conn, addr = s.accept()
        data = conn.recv(b_size)
        if not data:
            break
        else:
            print "received data from:%s data is:%s " % (name, data)
            # TODO check if data is type1:request name or type2: get data
            conn.send("Thanks got INFO at:"+str(time.time()))  # echo
    conn.close()
    return
    #except:
     #   print "no connection with:",ip
      #  return


def main(devices):
    slaves_threads = []
    for i in range(1,len(devices)):
        t = threading.Thread(target=receive_data_slave ,args=(i,devices,))
        slaves_threads.append(t)
        t.start()

    for t in slaves_threads:
        t.join()