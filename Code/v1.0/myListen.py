from gVariable import *
from iot_device import iot_device
import socket
import threading
import sub_functions
import time
import pickle
import main
from message import Message
from hc import HC


def start_sense(devices):
    sensor = HC(devices)
    sensor.get_delta_list()
    sensor.run(5)


def listen(devices,pid):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((sub_functions.my_ip_address(), TCP_PORT))
    s.listen(10)
    while True:
        try:
            conn, addr = s.accept()
            r = conn.recv(B_SIZE)
            if not r:
                break
            else:
                data = pickle.loads(r)
                if data.type == MESSAGE:
                    # log_message = "From: "+sub_functions.get_name_from_ip(addr[0],devices)
                    open(TRANSFER_FILE,"a").write(data.body+"\n")
                    print data.body
                #     enter data to log file
                elif data.type == DELTA_OF_DEVICE:
                    from hc import HC
                    senc = HC(devices)
                    senc.get_sample_from_ip(data.body,addr)
                elif data.type == CHANGE_MASTER:
                    print pid
                    open("master alive", 'w').write("F")
                    try:
                        if open("master alive", 'r').read() == "T":
                            devices = main.scan()
                            start_sense(devices)
                    except:
                        print "exit"
                        os.exit(0)
                elif data.type == GET_FROM_MASTER:
                    temp_data = data.body.split('|')
                    print "Update master, new master:\t"+temp_data[1]
                    master = iot_device(temp_data[1],temp_data[0],True)
                    if master < devices[0]:
                        devices[0].master = False
                        devices=[master]+devices
                        open("master alive", 'w').write("F")
                        start_sense(devices)
                    elif devices[0] != master:
                        massage = Message(master,None,GET_FROM_MASTER,devices[0].ip+"|"+devices[0].name)
                        sub_functions.send_message(massage)
                elif data.type == SENSOR_NOT_CONNECTED:
                    print data.body

                    # i_am_master = i_am__the_master()
                conn.close()
        except Exception,e:
            print e
            conn.close()
    conn.close()
