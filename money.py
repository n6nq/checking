""" money class  -- carries money as an integer. Multiplies and divides by 100 to
provide provide or consume presentations or strings"""

class Money(object):
    
    @classmethod
    def from_number(cls, number):
        obj = cls()
        print(type(number))
        obj.value = number
        return obj

    @classmethod
    def from_str(cls, amount_str):
        obj = cls()
        obj.value = int(float(amount_str) * 100)
        return obj
    
    @classmethod
    def str_to_num(cls, amount_str):
        return int(float(amount_str) * 100)
    
    def as_str(self):
        return '{}'.format(float(self.value) / 100)
    
    def value(self):
        return self.value
    
    def __gt__(self, other):
        return self.value > other.value
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __eq__(self, other):
        return self.value == other.value