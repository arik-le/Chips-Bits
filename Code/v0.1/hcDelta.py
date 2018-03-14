import mraa
import time
import sample
import pickle
import os.path

pin12 = mraa.Gpio(16)
pin12.dir(mraa.DIR_IN)  # echo
pin13 = mraa.Gpio(17)  # trig
pin13.dir(mraa.DIR_OUT)
# =====================================================================================
#                       get distance from the sensor
# =====================================================================================


def getDistance():
    while pin12.read() == 0:  # Check whether the ECHO is LOW
        p_start = time.time()  # Saves the last known time of LOW pulse

    while pin12.read() == 1:  # Check whether the ECHO is HIGH
        p_end = time.time()  # Saves the last known time of HIGH pulse

    p_duration = p_end - p_start  # Get pulse duration to a variable

    d = p_duration * 17150  # Multiply pulse duration by 17150 to get distance
    d = round(d, 2)  # Round to two decimal points
    return d


# =====================================================================================
#                         alert that error append
# =====================================================================================


def alert():
    print "Out Of Range"  # display out of range


# =====================================================================================
#                         create delta array from Sample
# =====================================================================================
def createDelta():
    deltas = [0, 0, 0]
    for i in range(len(myRanges)):
        if 0 < i < 8:
            delta = abs(myRanges[i].range - myRanges[i - 1].range)
            if delta > deltas[0]:
                deltas[0] = delta
        if 8 < i < 16:
            delta = abs(myRanges[i].range - myRanges[i - 1].range)
            if delta > deltas[1]:
                deltas[1] = delta
        if 16 < i < 24:
            delta = abs(myRanges[i].range - myRanges[i - 1].range)
            if delta > deltas[2]:
                deltas[2] = delta
    return deltas


# =====================================================================================
#                         reset the sensor
# =====================================================================================


def resetSensor():
    pin13.write(0)
    print "Waiting For Sensor To Settle"
    time.sleep(1)
    pin13.write(1)
    time.sleep(0.00001)
    pin13.write(0)
    return

# =====================================================================================
#                                   Sample class
# =====================================================================================


class Samples(object):
    def __init__(self, noc, list):
        self.noc = noc
        self.list = list
# =====================================================================================
#                         make samples arr
# =====================================================================================


def average(arr,s,f):
    total = 0
    print "#########################"
    for i in range(s,f):
        print i,"(",arr[i],")"
        total += arr[i]
    print "########",total/(f-s),"#######"
    return total/(f-s)


def create_samples(dif):
    print "==================================="
    resetSensor()
    temp=getDistance()
    print temp
    samples = [temp]
    noc = [0]
    for i in range(1,24):
        print i
        resetSensor()
        sample = getDistance()
        a=average(samples,noc[len(noc)-1],i)
        print a-dif,"<",sample,"<",a+dif
        if not a-dif < sample < a+dif:
            noc.append(i)
        print "i=",i," noc[",len(noc)-1,"]=",noc[len(noc)-1]
        samples.append(sample)
    s1 = Samples(noc,samples)
    add_to_file(s1,"sample")
    print noc
    print samples
    print "==================================="
    return s1

def get_from_file(file_name):
    data=None
    if os.path.isfile(file_name):
        f = open(file_name, "r")
        data=pickle.load(f)
        f.close()
    return data


def add_to_file(obj,file_name):
    f = open(file_name,"w")
    pickle.dump(obj,f,pickle.HIGHEST_PROTOCOL)
    f.close()


def get_samples():
    if not os.path.isfile("sample"):
        create_samples(5)
    else:
        s1= get_from_file("sample")
        print "noc=",s1.noc
        print "sample=",s1.list

print "Distance measurement in progress"
count = 0
avg = 0.0
myRanges = []
minDistance = 2
maxDistance = 400
print "Starting mesurement for templates"
time.sleep(2)
get_samples()
# create_samples(5)
# print get_from_file("sample")
# while count != 24:
#     resetSensor()
#     distance = getDistance()
#     print distance
#     if minDistance < distance < maxDistance:  # Check whether the distance is within range
#         measuremet = sample.make_sample(distance)  # create an Sample Object , constructor set range= distance
#         # create_sample(measuremet)
#         myRanges.append(measuremet)  # push to the end of the array
#         print "Distance:", distance, "cm, count is:", count  # Print distance with 0.5 cm calibration
#         count += 1
#     else:
#         alert()
#
# deltaArr = createDelta()
# for t in range(len(deltaArr)):
#     print "max delta in dellArr- ", t, "is:", deltaArr[t]
#
# time.sleep(3)
# count = 0
# previous = 0
#
# print "checking delta's"
# while count < 24:
#
#     resetSensor()
#     distance = getDistance()
#
#     if minDistance < distance < maxDistance:  # Check whether the distance is within range
#         if count == 0 or count == 8 or count == 16:
#             previous = distance
#         if 0 < count < 8:
#             if abs(distance - previous) > deltaArr[0]:
#                 print "cought CHANGE OF STATUS, Delta measurement is:", abs(
#                     distance - previous), "cm, and routine delta is:", deltaArr[0]
#                 break
#         if 8 < count < 16:
#             if abs(distance - previous) > deltaArr[1]:
#                 print "cought CHANGE OF STATUS, Delta measurement is:", abs(
#                     distance - previous), "cm, and routine delta is:", deltaArr[1]
#                 break
#         if 16 < count < 24:
#             if abs(distance - previous) > deltaArr[2]:
#                 print "cought CHANGE OF STATUS, Delta measurement is:", abs(
#                     distance - previous), "cm, and routine delta is:", deltaArr[2]
#                 break
#         print "mesurement is not upnormal,count is:", count
#         count += 1
#         previous = distance
#     else:
#         print "Out Of Range"  # display out of range
