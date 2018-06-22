import pickle
import os
from constant_variable import *


# class Message
class Message:
    def __init__(self,device, id, type, body):  # constructor
        # message will consist: type of message,content - body,device to send
        self.id = id
        self.type = type
        self.body = body
        self.device = device

    # add message to queue to send in proper order
    def add_to_queue(self):
        file = open(MESSAGE_QUEUE_FILE,"a")
        message_pickle=pickle.dumps(self)
        file.write(message_pickle+BUFFER)

    # update master
    def update_master(self,master):
        if self.device != master:
            self.device = master


# get message from queue
def get():
    new_file=open(MESSAGE_QUEUE_FILE,"r")
    message_list= new_file.read().split(BUFFER)
    return pickle.loads(message_list[0])


# take from file and cast it to object
def file_to_objects():
    if not exist():
        return []
    objects = []
    file = open(MESSAGE_QUEUE_FILE, "r")
    message_list = file.read().split(BUFFER)
    for message in message_list:
        objects.append(pickle.loads(message))
    return objects


# remove the message from queue
def remove_from_queue():
    if exist():
        file = open(MESSAGE_QUEUE_FILE, "r")
        message_list = file.read().split(BUFFER)
        file = open(MESSAGE_QUEUE_FILE, 'w')
        file.writelines(message_list[1:])

# check if there is a message in the queue
def exist():
    return os.stat(MESSAGE_QUEUE_FILE).st_size != 0


def update_queue(master):#update the master in file
    messages = file_to_objects()
    for message in messages:
        message.update_master(master)
    open(MESSAGE_QUEUE_FILE,'w').write("")
    for message in messages:
        message.add_to_queue()


