
class Sample(object):
    range = 0.0
    

    # The class "constructor" - It's actually an initializer 
    def __init__(self, range):
        self.range = range
        

def make_sample(range):
    sample = Sample(range)
    return sample 