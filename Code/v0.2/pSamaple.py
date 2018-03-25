class Sample(object):
    range = 0.0
    time = 0.0

    # The class "constructor" - It's actually an initializer
    def __init__(self, range,time):
        self.range = range
        self.time = time


def make_sample(range, time):
    sample = Sample(range,time)
    return sample