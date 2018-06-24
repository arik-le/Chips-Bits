from constant_variable import *
from iot_device import iot_device
import socket
import threading
import auxiliary_functions
import time
import pickle
import main
from message import Message
from hc import HC


# start sense data from the HC sensor
def start_sense(devices):
    sensor = HC(devices)
    sensor.get_delta_list()
    sensor.run(5)

# listen to messages from other devices
def listen(devices,pid):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((auxiliary_functions.my_ip_address(), TCP_PORT))
    s.listen(10)
    while True:
        try:
            conn, addr = s.accept()
            r = conn.recv(B_SIZE)
            if not r:
                break
            else:
                data = pickle.loads(r)
                if data.type == ERR_MESSAGE:  # error message
                    auxiliary_functions.add_to_log_file(data)   # enter data to log file
                    print data.body

                elif data.type == DELTA_OF_DEVICE:  # initial pattern of each device
                    from hc import HC
                    senc = HC(devices)
                    senc.get_sample_from_device(data.body,addr)
                elif data.type == CHANGE_MASTER:        # device is notice that master is fallen
                    open("master alive", 'w').write("F")
                    try:
                        if open("master alive", 'r').read() == "T":
                            devices = main.scan()
                            start_sense(devices)
                    except:
                        print "exit"
                        os.exit(0)
                elif data.type == GET_FROM_MASTER:      # get from device message that is the new master
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
                        auxiliary_functions.send_message(massage)
                elif data.type == SENSOR_NOT_CONNECTED:     # sensor not connected message
                    print data.body
                elif data.type == CHECKS_THAT_MASTER_IS_ALIVE:      # check if i (master) is alive
                    print data.body
                elif data.type == YOU_ARE_THE_MASTER:       # device that send me notify me that i am the master
                    devices[0].master =False
                    for device in devices:
                        if device.ip == auxiliary_functions.my_ip_address():
                            device.master = True
                            master = devices.pop(devices.index(device))
                    devices = [master] + sorted(devices,key=lambda iot_device: int(iot_device.ip.split('.')[3]))
                conn.send("get")
                    # i_am_master = i_am__the_master()
                conn.close()
        except Exception,e:
            print e
            conn.close()
    conn.close()
