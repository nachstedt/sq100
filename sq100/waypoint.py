class Waypoint(Point):
    TYPES = {
        0:  'DOT',
        1:  'HOUSE',
        2:  'TRIANGLE',
        3:  'TUNNEL',
        4:  'CROSS',
        5:  'FISH',
        6:  'LIGHT',
        7:  'CAR',
        8:  'COMM',
        9:  'REDCROSS',
        10: 'TREE',
        11: 'BUS',
        12: 'COPCAR',
        13: 'TREES',
        14: 'RESTAURANT',
        15: 'SEVEN',
        16: 'PARKING',
        17: 'REPAIRS',
        18: 'MAIL',
        19: 'DOLLAR',
        20: 'GOVOFFICE',
        21: 'CHURCH',
        22: 'GROCERY',
        23: 'HEART',
        24: 'BOOK',
        25: 'GAS',
        26: 'GRILL',
        27: 'LOOKOUT',
        28: 'FLAG',
        29: 'PLANE',
        30: 'BIRD',
        31: 'DAWN',
        32: 'RESTROOM',
        33: 'WTF',
        34: 'MANTARAY',
        35: 'INFORMATION',
        36: 'BLANK'
    }
    
    def __init__(self, latitude = 0, longitude = 0, altitude = 0, title = '', type = 0):
        self.altitude = altitude
        self.title = title
        self.type = type
        super(Waypoint, self).__init__(latitude, longitude) 
                
    def __str__(self):
        return "%s (%f,%f)" % (self.title, self.latitude, self.longitude)
        
    def __hex__(self):
        return "%(title)s00%(type)s%(altitude)s%(latitude)s%(longitude)s" % {
            'latitude'  : hex(self.latitude),
            'longitude' : hex(self.longitude),
            'altitude'  : Utilities.dec2hex(self.altitude,4),
            'type'      : Utilities.dec2hex(self.type,2),
            'title'     : Utilities.chr2hex(self.title.ljust(6)[:6])
        }
        
    def fromHex(self, hex):
        if len(hex) == 36:            
            def safeConvert(c):
                #if hex == 00 chr() converts it to space, not \x00
                if c == '00':
                    return ' '
                else:
                    return Utilities.hex2chr(c)
                
            self.latitude = Coordinate().fromHex(hex[20:28])
            self.longitude = Coordinate().fromHex(hex[28:36])
            self.altitude = Utilities.hex2signedDec(hex[16:20])
            self.title = safeConvert(hex[0:2])+safeConvert(hex[2:4])+safeConvert(hex[4:6])+safeConvert(hex[6:8])+safeConvert(hex[8:10])+safeConvert(hex[10:12])
            self.type = Utilities.hex2dec(hex[12:16])
            
            return self
        else:
            raise GH600ParseException(self.__class__.__name__, len(hex), 36)
