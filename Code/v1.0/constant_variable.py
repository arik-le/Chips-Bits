
MESSAGE_TO_MASTER_IS_ALIVETYPE = 0        # type of message
MESSAGE_BODY = 1

# type of messages #
ERR_MESSAGE = "1"
DELTA_OF_DEVICE = "2"
CHANGE_MASTER = "3"
GET_FROM_MASTER = "4"
SENSOR_NOT_CONNECTED = "5"
CHECKS_THAT_MASTER_IS_ALIVE = "6"
YOU_ARE_THE_MASTER = "7"

SAMPLES_MESSAGE ="2"

TRANSFER_FILE = "log"
MESSAGE_QUEUE_FILE = "message_queue"
MESSAGE_TO_MASTER_IS_ALIVE = "alive?"
TIME_TO_UPDATE = 60 #sec
BUFFER="[*********}"


TCP_PORT = 5005 # port number - can change
B_SIZE = 2048   # size of message


delay = 1           # delay between each messurements
offset = 5.0         # offset of delta
boot_time = 4       # boot time for senser to reset
