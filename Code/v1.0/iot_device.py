class iot_device():

    def __init__(self,name,ip,master):
        self.name = name
        self.ip = ip
        self.master = master

    def __str__(self):
        s= "Name is:"+self.name+" ,Ip is:"+self.ip
        if self.master:
            s+=" [Master]"
        return s

    def __lt__(self, other):
        this_lower = int(self.ip.split('.')[3])
        other_lower = int(other.ip.split('.')[3])
        print "56"
        return this_lower < other_lower

    def __ne__(self, other):
        return self.name != other.name and self.ip != other.ip

    def __eq__(self, other):
        return self.name == other.name and self.ip == other.ip

    def setMaster(self,master):
        self.master = master
