import pickle
import os
# from myListen import start_sense
from gVariable import *


class Message:
    def __init__(self,device, id, type, body):
        self.id = id
        self.type = type
        self.body = body
        self.device = device

    def add_to_queue(self):
        file = open(MESSAGE_QUEUE_FILE,"a")
        message_pickle=pickle.dumps(self)
        file.write(message_pickle+BUFFER)

    def update_master(self,master):
        if self.device != master:
            self.device = master


def get():
    file=open(MESSAGE_QUEUE_FILE,"r")
    message_list= file.read().split(BUFFER)
    return pickle.loads(message_list[0])


def file_to_objects():
    objects = []
    file = open(MESSAGE_QUEUE_FILE, "r")
    message_list = file.read().split(BUFFER)
    for message in message_list:
        objects.append(pickle.loads(message))
    return objects


def remove_from_queue():
    if exist():
        file = open(MESSAGE_QUEUE_FILE, "r")
        message_list = file.read().split(BUFFER)
        file = open(MESSAGE_QUEUE_FILE, 'w')
        file.writelines(message_list[1:])


def exist():
    return os.stat(MESSAGE_QUEUE_FILE).st_size != 0




