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
from  myListen import *
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
sensor_conncted = True


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
            print "Initial Pattern exist"
            print self.sample_str()
        else:
            self.create_delta_list()
            if len(self.delta_list) != 0:
                f = open(file_name, 'w')
                pickle.dump(self.delta_list, f)
                f = open(file_name, 'r')
                sm_message=Message(self.devices[0],None,SAMPLES_MESSAGE,self.delta_list)
                sub_functions.send_message(sm_message )

    def get_delta_from_file(self, adder):
        file = open(file_name + str(adder), 'r')
        return pickle.load(file)

    def create_delta_list(self):
        self.take_samples()
        if len(self.samples) == 0:
            return
        for i in range(1, len(self.samples) - 1):
            # print self.samples[i].range
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
        print self.sample_str()

    def sample_str(self):
        s = ''
        before_index = 0
        for delta in self.delta_list:
            if before_index !=delta['index']:
                s += '['+str(before_index)+'-'+str(delta['index'])+']'
            else:
                s += '[' + str(before_index)+']'
            s+="\taverage = "+str(delta['average'])+"\ttime + "+str(delta['time'])+'\n'
            before_index = delta["index"]+1
        return s

    def take_samples(self):
        print "Creating Initial Pattern"
        for i in range(24):
            m = self.get_measurement()
            if m == -1:
                break
            print "[", i, "]",m
            t = get_time()
            self.samples.append(sample.Sample(m, t))
            time.sleep(delay)

    def run(self, sample_range):
        global sensor_conncted
        master = self.devices[0]
        i_am_master=master.ip is sub_functions.my_ip_address()
        open("master alive","w").write("T")
        while open("master alive","r").read() == "T":
            sam = self.get_measurement()
            if sam is -1:
                print "No sensor is connected "
                if sensor_conncted:
                    sensor_conncted = False
            else:
                sensor_conncted = True
                print "Sample: ", sam
                if not self.is_in_range(5, sam):
                    if i_am_master:
                        print "Got an exception"
                    else:
                        pid = os.fork()
                        if pid is 0:

                            body = " Got an exception from " + socket.gethostname() + ": the measurement is:" + str(
                                sam) + " Routine measurement: " + \
                                      str(self.delta_list[0]["average"])
                            message = Message(master, None, MESSAGE, body)
                            self.send_in_fork(master, os.getpid(), 3, message)
                            print "Send the exception measurement"
                            os._exit(0)
                else:
                    print "O.K"
            try:
                time.sleep(sample_range)
            except:
                pass


    def is_in_range(self, range_s, sam):
        for d in self.delta_list:
            if float(d["average"]) - range_s < sam < float(d["average"]) + range_s:
                return True
        return False

    def send_in_fork(self, ip, pid, time_to_try, message):
        is_transfer = False
        print "Trying to send ", pid," Message"

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
            print "Message arrived", pid
        else:
            print "Message didn't arrived", pid
            print open("master alive", 'r').read()
            if open("master alive", 'r').read() == "T":
                for device in self.devices:
                    if device.ip is not sub_functions.my_ip_address():
                        cm_message=Message(device,None,CHANGE_MASTER,"mater does not respond ")
                        sub_functions.send_message(cm_message)
                open("master alive", 'w').write("F")
                from main import scan
                self.devices=scan()
                from myListen import start_sense
                start_sense(self.devices)

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