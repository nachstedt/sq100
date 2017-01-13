

class GH600Exception(Exception):
    pass


class GH600ParseException(GH600Exception):
    def __init__(self, what = None, length = None, expected = None):
        self.what = what
        self.length = length
        self.expected = expected
        
    def __str__(self):
        if self.what:
            return "Error parsing %s: Got %i, expected %i" % (self.what, self.length, self.expected) 
        else:
            return super(GH600ParseException, self).__str__()


class GH600SerialException(GH600Exception):
    pass
