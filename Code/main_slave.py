import hc
import sample
import socket
import os


def main(devices):
    x = hc.HC(devices)
    x.get_delta_list()
    x.run(5)
