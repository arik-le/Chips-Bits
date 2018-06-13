from gVariable import *
from iot_device import iot_device
import socket
import threading
import sub_functions
import time
import pickle
from message import Message
from hc import HC


def start_sense(devices):
    sensor = HC(devices)
    sensor.get_delta_list()
    sensor.run(5)


def listen(devices):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((sub_functions.my_ip_address(), TCP_PORT))
    s.listen(10)
    while True:
        print "listening"
        try:
            conn, addr = s.accept()
            r = conn.recv(B_SIZE)
            if not r:
                break
            else:
                data = pickle.loads(r)
                print type(data),data
                if data.type == MESSAGE:
                    print data.body
                elif data.type == DELTA_OF_DEVICE:
                    x = hc.HC(devices)
                    x.get_sample_from_ip(data.body,addr)
                elif data.type == CHANGE_MASTER:
                    f = open("master alive", 'w')
                    f.write("F")
                    from main import scan
                    devices=scan()
                    start_sense(devices)
                    break
                elif data.type == GET_FROM_MASTER:
                    print "update master"
                    temp_data=data.body.split('|')
                    master = iot_device(temp_data[1],temp_data[0],True)
                    if master < devices[0]:
                        devices[0].master = False
                        devices=[master]+devices
                        open("master alive", 'w').write("F")
                        start_sense(devices)
                    elif devices[0] != master:
                        print "2"
                        sub_functions.send_message(master.ip,GET_FROM_MASTER,devices[0].ip+"|"+devices[0].name)
                elif data.type == SENSOR_NOT_CONNECTED:
                    print data.body

                    # i_am_master = i_am__the_master()
                conn.close()
        except Exception,e:
            print e
            conn.close()
    conn.close()
