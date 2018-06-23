class Message:
    def __init__(self,device, id, type, body):
        self.id = id
        self.type = type
        self.body = body
        self.device = device
