""" money class  -- carries money as an integer. Multiplies and divides by 100 to
provide provide or consume presentations or strings"""

class Money(object):
    
    def __init__(self, str):
        self.value = int(float(str) * 100)

    def __init__(self, number):
        self.value = number
        
    def asStr(self):
        return '{}'.format(float(self.value) / 100)
        