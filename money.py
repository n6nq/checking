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
    
    def as_str(self):
        return '{}'.format(float(self.value) / 100)
    