class iot_device():   #represent  iot device

    # constructor - our variables for this protocol is name ip and boolean val = master
    def __init__(self,name,ip,master):
        self.name = name
        self.ip = ip
        self.master = master

    # str method
    def __str__(self):
        s= "Name is:"+self.name+" ,Ip is:"+self.ip
        if self.master:
            s+=" [Master]"
        return s

    # set master
    def setMaster(self, master):
        self.master = master

    # operator  <
    def __lt__(self, other):
        this_lower = int(self.ip.split('.')[3])
        other_lower = int(other.ip.split('.')[3])
        return this_lower < other_lower

    # operator !=
    def __ne__(self, other):
        return self.name != other.name and self.ip != other.ip

    #operator ==
    def __eq__(self, other):
        return self.name == other.name and self.ip == other.ip

