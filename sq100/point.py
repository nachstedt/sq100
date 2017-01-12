class Point(object):
    def __init__(self, latitude = 0, longitude = 0):
        self.latitude  = Coordinate(latitude)
        self.longitude = Coordinate(longitude)
        
    def __getitem__(self, attr):
        return getattr(self, attr)
        
    def __hex__(self):
        return '%s%s' % (hex(self.latitude), hex(self.longitude))
    
    def fromHex(self, hex):
        if len(hex) == 16:
            self.latitude = Coordinate().fromHex(hex[:8])
            self.longitude = Coordinate().fromHex(hex[8:])
            return self
        else:
            raise GH600ParseException(self.__class__.__name__, len(hex), 16)
