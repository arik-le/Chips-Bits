#! /usr/bin/env python


import subprocess
import ipaddress
import os
import threading
import time
import socket
import pexpect
import iot_device
import re
import master_main
import main_slave
# TODO create a file that run all imports and insatll them

########################### GLOBAL VALUES   #####################

devices = []    #IOT devices
threads = []   #ip threads to ping and check

# Prompt the user to input a network address
net_addr = u'192.168.43.0/24'

# Create the network
ip_net = ipaddress.ip_network(net_addr)

# Get all hosts on that network
all_hosts = list(ip_net.hosts())

# Configure subprocess to hide the console window
info = None
if os.name == 'nt':
    info = subprocess.STARTUPINFO()


#   return my ip address
def my_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    return my_ip


# use ssh command to remote device to return the device name
def ssh(host, cmd, user, password, timeout=10, bg_run=False):
    result = None
    try:
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        if bg_run:
            options += ' -f'
        ssh_cmd = 'ssh %s@%s %s "%s"' % (user, host, options, cmd)
        ssh_newkey = 'Are you sure you want to continue connecting'
        p = pexpect.spawn(ssh_cmd, timeout=timeout)

        i = p.expect([ssh_newkey, 'password:', pexpect.EOF])
        if i == 0:
            p.sendline('yes')
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
        my_ips = str(my_ip_address())
        if my_ips != ip:
            print "check for IP: ", ip
            name = ssh(ip,'uname -n','root','123456')
            if name != 'Unknown':
                name = re.sub("[^a-zA-Z0-9]", '',name)
                print name
                devices.append(iot_device.iot_device(name, ip, False))
        return


################################# MAIN ################################


#   run 255 threads to ping and check who is active
for i in range(1,len(all_hosts),25):
    for j in range(i,i+25):
        print i,j
        t = threading.Thread(target=ping_host,args=(j,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
        print('Thread {} Stopped'.format(t))


# join and wait until all threads are finished
for t in threads:
    t.join()
    print('Thread {} Stopped'.format(t))
print "after join"
#   appand my device and sort by ip
devices.append(iot_device.iot_device(socket.gethostname(), my_ip_address(), False))
devices = sorted(devices, key=lambda iot_device: iot_device.ip)
devices[0].master = True    #the lowest ip is the master

#   temp print
for h in devices:
    print h

#   check if my device is the master
if devices[0].ip == my_ip_address():
    print "i am master"
    master_main.main(devices)   #run master main function
else:
    print "i am slave"
    main_slave.main(devices)






