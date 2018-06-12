#! /usr/bin/env python
#   python main.py
import subprocess

try:
    import ipaddress
except:
    print "install ipaddress"
    subprocess.call("pip install ipaddress", shell=True)
    import ipaddress

try:
    import pexpect
except:
    print "install pexpect"
    subprocess.call("pip install pexpect", shell=True)
    import pexpect

import os
import threading
import time
import socket
import iot_device
import re
import master_main
import main_slave
import sub_functions
from message import Message
from myListen import listen
from ms import ms
from gVariable import *
# TODO create a file that run all imports and insatll them

########################### GLOBAL VALUES   #####################

devices = []    #IOT devices
threads = []   #ip threads to ping and check
pos_ips = []


# remove all known hosts and copy backup at known_hosts-old
try:
    subprocess.call("cp -av ~/.ssh/known_hosts ~/.ssh/known_hosts-old", shell=True)
    subprocess.call("rm ~/.ssh/known_hosts", shell=True)
except Exception,e:
    print "not needed to delete known hosts"

# Prompt the user to input a network address

net_addr =sub_functions.get_range()
# u'192.168.43.0/24'

# Create the network
ip_net = ipaddress.ip_network(net_addr)

# Get all hosts on that network
all_hosts = list(ip_net.hosts())

# Configure subprocess to hide the console window
info = None
if os.name == 'nt':
    info = subprocess.STARTUPINFO()


# use ssh command to remote device to return the device name
def ssh(host, cmd, user, password, timeout=10, bg_run=False):
    result = None
    try:
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        if bg_run:
            options += ' -f'
        ssh_cmd = 'ssh %s@%s %s "%s"' % (user, host, options, cmd)
        ssh_newkey = 'Do you want to continue connecting?'
        p = pexpect.spawn(ssh_cmd, timeout=timeout)

        i = p.expect([ssh_newkey, 'password:', pexpect.EOF])
        if i == 0:
            p.sendline('y')
            i = p.expect([ssh_newkey, 'password:', pexpect.EOF])
        if i == 1:
            p.sendline(password)
            p.expect(pexpect.EOF)
            result = p.before  # print out the result
        elif i == 2:
            result = 'Unknown'
            print "either got key or connection timeout"
    except:
        result = 'Unknown'
        print "timeout exceeded probably not a Iot Device"
    return result


#   ping function to run on any host in the LAN

def ping_host(i):
    output = subprocess.Popen(['ping', '-c', '1', '-w', '1', str(all_hosts[i])], stdout=subprocess.PIPE,
                              startupinfo=info).communicate()[0]
    if " 0 packets received, 100% packet loss" in output.decode('utf-8'):
        return  # print(str(all_hosts[i]), "is Offline")
    elif "Request timed out" in output.decode('utf-8'):
        return  # print(str(all_hosts[i]), "is Offline")
    else:
        ip = str(all_hosts[i])
        my_ips = str(sub_functions.my_ip_address())
        if my_ips != ip:
            pos_ips.append(ip)
        return


def ssh_start(ip):
    name = ssh(ip,'uname -n','root','123456')
    if name != 'Unknown':
        name = re.sub("[^a-zA-Z0-9]", '',name)
        print name
        devices.append(iot_device.iot_device(name, ip, False))
    return


def route():
    #   check if my device is the master
    if devices[0].ip == sub_functions.my_ip_address():
        print "i am Master"
        master_main.main(devices)   #run master main function
    else:
        print "i am Slave"
        main_slave.main(devices)
################################# MAIN ################################


def scan():
    global threads
    global devices
    #   run 255 threads to ping and check who is active
    for i in range(0, 11):
        s = v = 25
        if i == 10:
            v = 4
        for j in range(i*s, (i * s) + v):
            t = threading.Thread(target=ping_host,args=(j,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        threads = []

    # run threads on the active ip's in the LAN to get NAME
    for i in range(len(pos_ips)):
        t = threading.Thread(target=ssh_start,args=(pos_ips[i],))
        threads.append(t)
        t.start()

    for t in threads:
            t.join()

    threads = []

    #  append my device and sort by ip
    devices.append(iot_device.iot_device(socket.gethostname(), sub_functions.my_ip_address(), False))
    devices = sorted(devices, key=lambda iot_device: iot_device.ip)
    devices[0].master = True    #the lowest ip is the master

    #   temp print
    print "==============="
    for device in devices:
        print device
    print "==============="
    if devices[0].ip == sub_functions.my_ip_address():
        for device in devices[1:]:
            message = Message(device,None,GET_FROM_MASTER,devices[0].ip+'|'+devices[0].name)
            sub_functions.send_message(message)
    return devices


def i_am__the_master():
    if sub_functions.my_ip_address() == devices[0].ip:
        return True
    return False


if __name__ == '__main__':
    scan()
    pid = os.fork()
    if pid is 0:
        print "son"
        ms(devices)
    else:
        print "father"
        listen(devices)
    # lis = threading.Thread(target=listen, args=(devices,i_am__the_master(),))
    # lis.start()11111
    # sen = threading.Thread(target=ms, args=(devices, i_am__the_master(),))
    # sen.start()






