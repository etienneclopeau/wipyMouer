
import uos

class Smoother():
    def __init__(self, windowLength = 20):
        self.lastValues = list()
        self.windowLength = windowLength
    
    def smoothThis(self, value):
        self.lastValues.append(value)
        if len(self.lastValues) > self.windowLength: 
            self.lastValues.pop(0)
        return sum(self.lastValues) / len(self.lastValues)

def random(min, max):
    return uos.urandom(1)[0] / 256 * (max-min) + min
