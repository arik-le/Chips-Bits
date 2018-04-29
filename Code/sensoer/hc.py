import mraa
import time
import sample
import pickle
import os.path
import sensors
import time
import datetime
import socket
from iot_device import iot_device


TCP_PORT = 5005
pin12 = mraa.Gpio(16)
pin12.dir(mraa.DIR_IN)  # echo
pin13 = mraa.Gpio(17)  # trig
pin13.dir(mraa.DIR_OUT)
file_name = "hcSample"
delay = 1
delta = 5.0


class HC(sensors.Sensor):
    def __init__(self,devices):
        self.samples = []
        self.delta_list = []
        self.neighbors_list = devices

    def get_measurement(self):
        self.reset_sensor()
        while pin12.read() == 0:  # Check whether the ECHO is LOW
            p_start = time.time()  # Saves the last known time of LOW pulse

        while pin12.read() == 1:  # Check whether the ECHO is HIGH
            p_end = time.time()  # Saves the last known time of HIGH pulse

        p_duration = p_end - p_start  # Get pulse duration to a variable

        d = p_duration * 17150  # Multiply pulse duration by 17150 to get distance
        d = round(d, 2)  # Round to two decimal points
        return d

    def reset_sensor(self):
        pin13.write(0)
        print "Waiting For Sensor To Settle"
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
            file = open(file_name, 'w')
            pickle.dump(self.delta_list, file)

    def get_delta_from_file(self,adder):
        file = open(file_name+str(adder), 'r')
        return pickle.load(file)

    def create_delta_list(self):
        self.take_samples()

        for i in range(1, len(self.samples) - 1):
            print self.samples[i].range
            before_item = self.samples[i - 1].range
            item = self.samples[i].range
            if abs(item - before_item) > delta:
                j = 0
                if len(self.delta_list) > 0:
                    j = self.delta_list[-1]["index"]
                self.delta_list.append({'time': self.samples[i].time,'index': i,"average":'%.2f' % get_average(self.samples,j, i)})
        j = 0
        if len(self.delta_list) > 0:
            j = self.delta_list[-1]["index"]
        i = len(self.samples) - 1
        self.delta_list.append({'time': get_time(), 'index':i , "average": get_average(self.samples, j, i)})
        print self.delta_list

    def take_samples(self):
        for i in range(6):
            print "======", i, "========"
            m = self.get_measurement()
            t = get_time()
            self.samples.append(sample.Sample(m, t))
            time.sleep(delay)

    def run(self,sample_range,hc_is_connect):
        # self.neighbors_list.append(iot_device("D2", "192.168.43.154", False))
        # self.neighbors_list.append(iot_device("D1", "192.168.43.151", True))
        master= self.neighbors_list[0]
        print master
        if my_ip()is not self.neighbors_list[0]:
            while True:
                if hc_is_connect:
                    sam = self.get_measurement()
                    if not self.get_sample_by_time(5,sam):
                        print "out of range"
                        while True:
                            try:
                                print self.send_message("problem",master.ip)
                                break
                            except socket.error, exc:
                                print str(exc)
                    else:
                        try:
                            print self.send_message(str(sam),master.ip)
                            print master.ip
                        except socket.error, exc:
                            print "connection lost: "+str(exc)
                        print "O.K"
                    time.sleep(sample_range)
                else:
                    self.send_message("hc isnt connect")
        else:
            print "i am the master"

    def get_sample_by_time(self,range_s,sam):#return the sample are we want to compare
        # this_time=get_time()
        for d in self.delta_list:
            if d["average"]-range_s < sam < d["average"]+range_s:
                return True
        return False

    def send_message(self,message,ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((ip, TCP_PORT))
        print ip
        print TCP_PORT
        s.send(message)
        s.settimeout(5)
        data = s.recv(2048)
        s.close()
        return data

    def send_samples(self, ip):
        file = open(file_name)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, TCP_PORT))
        data = file.read()
        s.send(data)
        s.settimeout(5)
        data = s.recv(2048)
        print data
        s.close()

    def get_sample_from_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((my_ip(), TCP_PORT))
        s.listen(5)
        conn,addr=s.accept()
        while True:
            samples = conn.recv(2048)
            if not samples:
                break
            addr_res = str(addr[0])
            file = open(file_name+"_"+addr_res, 'w')
            file.write(samples)
            conn.send("v")
            file.close()
            m= self.get_delta_from_file("_"+addr_res)
        conn.close()
        s.close()

def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    return ip

def get_time():
    now = datetime.datetime.now()
    return str(now.hour)+":"+ str(now.minute)+":"+str(now.second)


def get_average(samples,s,f):
    total=0.0
    for i in range(s,f):
        total += samples[i].range
    return total/(f-s)