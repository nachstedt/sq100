class Lap(object):
    def __init__(self, start = datetime.datetime.now(), end = datetime.datetime.now(), duration = datetime.timedelta(), distance = 0, calories = 0,
                 startPoint = Point(0,0), endPoint = Point(0,0)):
        self.start        = start
        self.end          = end
        self.duration     = duration
        self.distance     = distance
        self.calories     = calories
        
        self.startPoint   = startPoint
        self.endPoint     = endPoint
        
    def __getitem__(self, attr):
        return getattr(self, attr)

    def fromHex(self, hex):
        if len(hex) == 44:
            self.__until   = Utilities.hex2dec(hex[:8])
            self.__elapsed = Utilities.hex2dec(hex[8:16])
            self.distance = Utilities.hex2dec(hex[16:24])
            self.calories = Utilities.hex2dec(hex[24:28])
 
            return self
        else:
            raise GH600ParseException(self.__class__.__name__, len(hex), 44)
        
    def calculateDate(self, date):
        self.end = date + datetime.timedelta(milliseconds = (self.__until * 100))
        self.start = self.end - datetime.timedelta(milliseconds = (self.__elapsed * 100))
        self.duration = self.end - self.start
        
    def calculateCoordinates(self, trackpoints):
        relative_to_start = relative_to_end = {}
        
        for trackpoint in trackpoints:
            relative_to_start[abs(self.start - trackpoint.date)] = trackpoint
            relative_to_end[abs(self.end - trackpoint.date)] = trackpoint
            
        nearest_start_point = relative_to_start[min(relative_to_start)]
        nearest_end_point = relative_to_end[min(relative_to_end)]
    
        self.startPoint = Point(nearest_start_point.latitude, nearest_start_point.longitude)
        self.endPoint = Point(nearest_end_point.latitude, nearest_end_point.longitude)
