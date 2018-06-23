

class Sample(object):
    range = 0.0
    time = ""

    # The class "constructor" - It's actually an initializer
    def __init__(self, range,time):
        self.range = range
        self.time = time

    def __str__(self):
        return "range: "+str(self.range)+",time: "+str(self.time)

def make_sample(range, time):
    sample = Sample(range,time)
    return sample