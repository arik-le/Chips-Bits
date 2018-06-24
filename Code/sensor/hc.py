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
TCP_PORT = 5005
pin12 = mraa.Gpio(16)
pin12.dir(mraa.DIR_IN)  # echo
pin13 = mraa.Gpio(17)  # trig
pin13.dir(mraa.DIR_OUT)
file_name = "hcSample"
delay = 1
delta = 5.0
boot_time = 4

class HC(sensors.Sensor):
    def __init__(self,devices):
        self.samples = []
        self.delta_list = []
        self.devices=devices

    def get_measurement(self):
        self.reset_sensor()
        timeout = time.time() + boot_time
        while pin12.read() == 0:    # Check whether the ECHO is LOW
            if time.time() > timeout:
                return -1
            p_start = time.time()  # Saves the last known time of LOW pulse

        while pin12.read() == 1:  # Check whether the ECHO is HIGH
            p_end = time.time()  # Saves the last known time of HIGH pulse

        p_duration = p_end - p_start  # Get pulse duration to a variable

        d = p_duration * 17150  # Multiply pulse duration by 17150 to get distance
        d = round(d, 2)  # Round to two decimal points
        print d
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

    def run(self,sample_range):
        master = self.devices[0].ip
        while True:
            sam = self.get_measurement()
            print "sam:",sam
            if sam is -1:
                print "hc not connect"
            else:
                if not self.is_in_range(5,sam):
                    pid = os.fork()
                    if pid is 0:
                        self.send_in_fork(master,os.getpid(),3)
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
    def is_in_range(self,range_s,sam):#return the sample are we want to compare
        for d in self.delta_list:
            if float(d["average"])-range_s < sam < float(d["average"])+range_s:
                return True
        return False

    def send_in_fork(self,ip,pid,time_to_try):
        is_transfer=False
        print "i try to send",pid
        for i in range(time_to_try):
            try:
                print sub_functions.send_message(ip,"problem result from pid :"+str(pid))
                is_transfer=True
                break
            except socket.error,e:
                 print e,os.getpid()
        if is_transfer:
            print "message arrived",pid
        else:
            print "message not arrived",pid

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
        s.bind((sub_functions.my_ip_address(), TCP_PORT))
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
        conn.close()
        s.close()



def get_time():
    now = datetime.datetime.now()
    return str(now.hour)+":"+ str(now.minute)+":"+str(now.second)


def get_average(samples,s,f):
    total=0.0
    for i in range(s,f):
        total += samples[i].range
    return total/(f-s)