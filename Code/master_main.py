#! /usr/bin/env python
import pickle
import threading
import socket
import time
import datetime
import hc
import sub_functions


SEPARATION = "$$$"
tcp_port = 5005
b_size = 2048  # Normally 2048, but we want fast response

is_slave = False




# receive data from slave function - run for each slave as a thread function
def receive_data_slave(devices):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((sub_functions.my_ip_address(), tcp_port))
    s.listen(10)
    while True:
        print "listening"
        try:
            conn, addr = s.accept()
            r = conn.recv(b_size)
            if not r:
                break
            else:
                data =  pickle.loads(r)
                print "####"
                print data[0]
                print "####"
                if data[0] == "1":
                    print data[1]
                elif data[0] == "2":
                    print "hhh"
                    x = hc.HC(devices)
                    x.get_sample_from_ip(data[1],addr)
                elif data[0] == "3":
                    if addr[0].ip < sub_functions.my_ip_address():
                        print "i am now slave, the Master is: %s" %(str(addr[0].ip))
                        devices[0].master = False
                        devices.append(iot_device.iot_device(socket.gethostname(), sub_functions.my_ip_address(), True))
                        devices = sorted(devices, key=lambda iot_device: iot_device.ip)
                        global is_slave
                        is_slave = True
                        break
                conn.close()
                conn.send("Master: Thanks got INFO at:"+str(datetime.datetime.now()))  # echo
        except Exception,e:
            print e
            conn.close()
    conn.close()
    if is_slave is True:
        main.route()
    return


def send_to_all(devices):
    threads = []
    msg = "I am Master"
    print msg + "send all"
    for i in range(1,len(devices)):
        t = threading.Thread(target=sub_functions.send_message, args=(devices[i].ip, "3", msg,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()




def main(devices):
    send_to_all(devices)
    receive_data_slave(devices)
