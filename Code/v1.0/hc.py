import mraa
import time
import sample
import pickle
import os.path
import os
import sensors
import time
import datetime
import socket
import sub_functions
from gVariable import *
from message import Message
from data_package import DataPackage

# TCP_PORT = 5005
pin12 = mraa.Gpio(16)
pin12.dir(mraa.DIR_IN)  # echo
pin13 = mraa.Gpio(17)  # trig
pin13.dir(mraa.DIR_OUT)
file_name = "hcSample"
delay = 1
delta = 5.0
boot_time = 4


class HC(sensors.Sensor):
    def __init__(self, devices):
        self.samples = []
        self.delta_list = []
        self.devices = devices

    def get_measurement(self):
        self.reset_sensor()
        timeout = time.time() + boot_time
        while pin12.read() == 0:  # Check whether the ECHO is LOW
            if time.time() > timeout:
                return -1
            p_start = time.time()  # Saves the last known time of LOW pulse

        while pin12.read() == 1:  # Check whether the ECHO is HIGH
            p_end = time.time()  # Saves the last known time of HIGH pulse

        p_duration = p_end - p_start  # Get pulse duration to a variable

        d = p_duration * 17150  # Multiply pulse duration by 17150 to get distance
        d = round(d, 2)  # Round to two decimal points

        return d

    def reset_sensor(self):
        pin13.write(0)
        pin13.write(1)
        time.sleep(0.00001)
        pin13.write(0)
        return

    def get_delta_list(self):
        if sensors.file_exist(file_name):
            self.delta_list = self.get_delta_from_file("")
            print self.delta_list
        else:
            self.create_delta_list()
            if len(self.delta_list) != 0:
                f = open(file_name, 'w')
                pickle.dump(self.delta_list, f)
                f = open(file_name, 'r')
                sm_message=Message(devices[0],SAMPLES_MESSAGE,self.delta_list)
                sub_functions.send_message(sm_message )

    def get_delta_from_file(self, adder):
        file = open(file_name + str(adder), 'r')
        return pickle.load(file)

    def create_delta_list(self):
        self.take_samples()
        if len(self.samples) == 0:
            return
        for i in range(1, len(self.samples) - 1):
            print self.samples[i].range
            before_item = self.samples[i - 1].range
            item = self.samples[i].range
            if abs(item - before_item) > delta:
                j = 0
                if len(self.delta_list) > 0:
                    j = self.delta_list[-1]["index"]
                self.delta_list.append(
                    {'time': self.samples[i].time, 'index': i, "average": '%.2f' % get_average(self.samples, j, i)})
        j = 0
        if len(self.delta_list) > 0:
            j = self.delta_list[-1]["index"]
        i = len(self.samples) - 1
        self.delta_list.append({'time': get_time(), 'index': i, "average": get_average(self.samples, j, i)})
        print self.delta_list

    def take_samples(self):
        for i in range(6):
            print "======", i, "========"
            m = self.get_measurement()
            if m == -1:
                break
            t = get_time()
            self.samples.append(sample.Sample(m, t))
            time.sleep(delay)

    def run(self, sample_range):
        print "start senc"
        master = self.devices[0]
        i_am_master=master.ip is sub_functions.my_ip_address()
        open("master alive","w").write("T")
        while open("master alive","r").read() == "T":
            sam = self.get_measurement()
            print "sam:", sam
            if sam is -1:
                print "hc not connect "
            else:
                if not self.is_in_range(5, sam):
                    if i_am_master:
                        print "get problem from my sensor"
                    else:
                        pid = os.fork()
                        if pid is 0:

                            body = " get problem from " + socket.gethostname() + ": the measurement is:" + str(
                                sam) + " need to be around: " + \
                                      str(self.delta_list[0]["average"])
                            message = Message(master, None, MESSAGE, body)
                            self.send_in_fork(master, os.getpid(), 3, message)
                            print "send the problem"
                            os._exit(0)
                            print "not dead!!!!!!!"
                        else:
                            print "main keep running"
                else:
                    print "O.K"
            try:
                time.sleep(sample_range)
            except:
                pass
        print "close senc"

    def is_in_range(self, range_s, sam):
        # TODO return the sample are we want to compare
        for d in self.delta_list:
            if float(d["average"]) - range_s < sam < float(d["average"]) + range_s:
                return True
        return False

    def send_in_fork(self, ip, pid, time_to_try, message):
        is_transfer = False
        print "i try to send", pid

        for i in range(time_to_try):
            try:
                res = sub_functions.send_message(message)
                if res is not None:
                    is_transfer = True
                break
            except socket.error, e:
                time.sleep(0.01)
                print e, os.getpid()
        if is_transfer is True:
            print "message arrived", pid
        else:
            print "message not arrived", pid
            for device in self.devices:
                if device.ip is not sub_functions.my_ip_address():
                    cm_message=Message(device,None,CHANGE_MASTER,"mater does not respond ")
                    sub_functions.send_message(cm_message)
            f = open("master alive", 'w')
            f.write("F")
            from main import scan
            self.devices=scan()
            from ms import ms
            ms(self.devices)
            # is_master = sub_functions.check_is_alive(self.devices)
            # if is_master:  # master has fallen and now this slave is the new master
            #
            #     main.route()

    def send_samples(self, ip):
        file = open(file_name)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, TCP_PORT))
        data = file.read()
        s.send(DataPackage.SAMPLES_MESSAGE + data)
        s.settimeout(5)
        data = s.recv(2048)
        print data
        s.close()

    def get_sample_from_ip(self, samples, addr):
        addr_res = str(addr[0])
        print file_name + "_" + addr_res
        try:
            file = open(file_name + "_" + addr_res, 'wb')
            pickle.dump(samples, file)
        except Exception as e:
            print e
        # file.close()


def get_time():
    now = datetime.datetime.now()
    return str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)


def get_average(samples, s, f):
    total = 0.0
    for i in range(s, f):
        total += samples[i].range
    return total / (f - s)