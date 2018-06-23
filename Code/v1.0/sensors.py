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
    # def set_sample(self):
    #     pass
    #
    # def create_sample(self):
    #     pass

    def get_measurement(self):
        pass

    def reset_sensor(self):
        pass

    def get_samples(self):
        pass