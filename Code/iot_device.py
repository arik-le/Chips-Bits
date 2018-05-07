class iot_device():

    def __init__(self,name,ip,master):
        self.name = name
        self.ip = ip
        self.master = master

    def toString (self):
        return "Name is:"+self.name+" ,Ip is:"+self.ip+" ,is Master?"+self.master

    def setMaster(self,master):
        self.master = master
