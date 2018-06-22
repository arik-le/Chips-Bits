import pickle
import os.path
from abc import ABCMeta, abstractmethod


def get_from_file(file_name):
    data = None
    if os.path.isfile(file_name):
        f = open(file_name, "r")
        data = pickle.load(f)
        f.close()
    return data


def add_to_file(obj, file_name):
    f = open(file_name, "w")
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    f.close()


def file_exist(file_name):
    return os.path.isfile(file_name)


class Sensor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_measurement(self):
        pass

    def reset_sensor(self):
        pass

    def get_samples(self):
        pass

    def __init__(self):
        pass


    def get_delta_list(self):
        pass

    def get_delta_from_file(self, adder):
        pass

    def create_delta_list(self):
        pass

    def sample_str(self):
        pass

    def take_samples(self):
        pass

    def run(self, sample_range):
        pass

    def is_in_range(self, range_s, sam):
      pass

    def send_in_fork(self, ip, pid, time_to_try, message):
        pass

    def send_samples(self, ip):
        pass

    def get_sample_from_device(self, samples, addr):
        pass
