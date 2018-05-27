import socket
import threading
import sub_functions
import time
import pickle
from hc import HC

TCP_PORT = 5005
b_size = 2048
threads = []
is_master = False

def main(devices):
    lis = threading.Thread(target=listening, args=devices, )
    lis.start()
    sen = threading.Thread(target=sense, args=(devices,))
    sen.start()


def sense(devices):
    x = HC(devices)
    x.get_delta_list()
    x.run(5)


def listening(devices):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((sub_functions.my_ip_address(), TCP_PORT))
    s.listen(10)
    while True:
        print "listening"
        try:
            conn, addr = s.accept()
            r = conn.recv(b_size)
            if not r:
                break
            else:
                data = pickle.loads(r)
                if data[0] == "3":
                    print data[1] + " from: " + str(addr[0].ip)
                    devices[0].master = False
                    devices.append(iot_device.iot_device(socket.gethostname(), sub_functions.my_ip_address(), True))
                    devices = sorted(devices, key=lambda iot_device: iot_device.ip)
                    if devices[0].ip == sub_functions.my_ip_address():
                        print "I a the Master Now"
                        global is_master
                        is_master = True
                        break
                        # print data
            time.sleep(15)
        except:
            conn.close()
    if is_master is True:
        conn.close()
        main.route()
    return





