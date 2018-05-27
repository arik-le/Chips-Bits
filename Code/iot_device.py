class iot_device():

    def __init__(self,name,ip,master):
        self.name = name
        self.ip = ip
        self.master = master


    def __str__(self):
        return "Name is:"+self.name+" ,Ip is:"+self.ip+" ,is Master?"+str(self.master)

    def setMaster(self,master):
        self.master = master
