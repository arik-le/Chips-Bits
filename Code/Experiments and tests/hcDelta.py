import mraa
import time
import sample

pin12 = mraa.Gpio(16)
pin12.dir(mraa.DIR_IN)  # echo
pin13 = mraa.Gpio(17)  # trig
pin13.dir(mraa.DIR_OUT)
print "Distance measurement in progress"
count = 0
avg = 0.0
myRanges = []

x=6
print "Starting mesurement for templates"
time.sleep(2)

while count != 24 :
    pin13.write(0)
    print "Waiting For Sensor To Settle"
    time.sleep(1)
    pin13.write(1)
    time.sleep(0.00001)
    pin13.write(0)

    while pin12.read() == 0:  # Check whether the ECHO is LOW
        pulse_start = time.time()  # Saves the last known time of LOW pulse

    while pin12.read() == 1:  # Check whether the ECHO is HIGH
        pulse_end = time.time()  # Saves the last known time of HIGH pulse

    pulse_duration = pulse_end - pulse_start  # Get pulse duration to a variable

    distance = pulse_duration * 17150  # Multiply pulse duration by 17150 to get distance
    distance = round(distance, 2)  # Round to two decimal points

    if 2 < distance < 400:  # Check whether the distance is within range
        measuremet = sample.make_sample(distance)  # create an Sample Object , constructor set range= distance
        myRanges.append(measuremet)  # push to the end of the array
        print "Distance:", distance, "cm, count is:",count  # Print distance with 0.5 cm calibration
        count += 1
    else:
        print "Out Of Range , recalibrate"  # display out of range

delArr = [0,0,0]


for i in range(len(myRanges)):
    if 0 < i < 8:
        delta = abs(myRanges[i].range - myRanges[i-1].range)
        if delta > delArr[0]:
            delArr[0]=delta
    if 8 < i < 16:
        delta = abs(myRanges[i].range - myRanges[i - 1].range)
        if delta > delArr[1]:
            delArr[1] = delta
    if 16 < i < 24:
        delta = abs(myRanges[i].range - myRanges[i - 1].range)
        if delta > delArr[2]:
            delArr[2] = delta
for t in range(3):
    print "max delta in dellArr- ",t,"is:",delArr[t]

time.sleep(3)

count =0
newArr = [1]

print "checking delta's"
while count < 24:

    pin13.write(0)
    print "Waiting For Sensor To Settle"
    time.sleep(1)
    pin13.write(1)
    time.sleep(0.00001)
    pin13.write(0)

    while pin12.read() == 0:  # Check whether the ECHO is LOW
        pulse_start = time.time()  # Saves the last known time of LOW pulse

    while pin12.read() == 1:  # Check whether the ECHO is HIGH
        pulse_end = time.time()  # Saves the last known time of HIGH pulse

    pulse_duration = pulse_end - pulse_start  # Get pulse duration to a variable

    distance = pulse_duration * 17150  # Multiply pulse duration by 17150 to get distance
    distance = round(distance, 2)  # Round to two decimal points

    if 2 < distance < 400:  # Check whether the distance is within range
        if count == 0 or count==8 or count==16:
            newArr[0]= distance
        if 0 < count < 8:
            if abs(distance- newArr[0]) > delArr[0]:
                print "cought CHANGE OF STATUS, Delta measurement is:", abs(distance- newArr[0]), "cm, and routine delta is:", delArr[0]
                break
        if 8 < count < 16:
            if abs(distance- newArr[0]) > delArr[1]:
                print "cought CHANGE OF STATUS, Delta measurement is:", abs(distance- newArr[0]), "cm, and routine delta is:", delArr[1]
                break
        if 16 < count < 24:
            if abs(distance- newArr[0]) > delArr[2]:
                print "cought CHANGE OF STATUS, Delta measurement is:", abs(distance- newArr[0]), "cm, and routine delta is:", delArr[2]
                break
        print "mesurement is not upnormal,count is:",count
        count+=1
		newArr[0]= distance
    else:
        print "Out Of Range"  # display out of range
