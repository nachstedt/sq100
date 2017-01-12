class Trackpoint(Point):    
    def __init__(self, latitude = 0, longitude = 0, altitude = 0, speed = 0, heartrate = 0, interval = datetime.timedelta(), date = datetime.datetime.utcnow()):
        self.altitude    = altitude
        self.speed       = speed
        self.heartrate   = heartrate
        self.interval    = interval
        self.date        = date
        super(Trackpoint, self).__init__(latitude, longitude)
    
    def __getitem__(self, attr):
        return getattr(self, attr)
        
    def __str__(self):
        return "(%f, %f, %i, %i, %i, %i)" % (self.latitude, self.longitude, self.altitude, self.speed, self.heartrate, self.interval)
    
    def __hex__(self):            
        return "%(latitude)s%(longitude)s%(altitude)s%(speed)s%(heartrate)s%(interval)s" % {
            'latitude':   hex(self.latitude),
            'longitude':  hex(self.longitude),
            'altitude':   Utilities.dec2hex(self.altitude,4),
            'speed':      Utilities.dec2hex(self.speed,4),
            'heartrate':  Utilities.dec2hex(self.heartrate,2),
            'interval':   Utilities.dec2hex(self.interval.microseconds/1000,4)
        }
        
    def fromHex(self, hex):
        if len(hex) == 30:
            self.latitude  = Coordinate().fromHex(hex[0:8])
            self.longitude = Coordinate().fromHex(hex[8:16])
            self.altitude  = Utilities.hex2signedDec(hex[16:20])
            self.speed     = Utilities.hex2dec(hex[20:24])/100
            self.heartrate = Utilities.hex2dec(hex[24:26])
            self.interval  = datetime.timedelta(seconds=Utilities.hex2dec(hex[26:30])/10.0)       
             
            return self
        else:
            raise GH600ParseException(self.__class__.__name__, len(hex), 30)
    
    def calculateDate(self, date):
        self.date = date + self.interval
