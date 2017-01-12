import datetime
import pytz


class Track(object):    
    def __init__(self, date = datetime.datetime.utcnow(), duration = datetime.timedelta(), distance = 0, calories = 0, topspeed = 0, trackpointCount = 0, id=0):
        self.id              = id
        self.date            = date
        self.duration        = duration
        self.distance        = distance
        self.calories        = calories
        self.topspeed        = topspeed
        self.trackpointCount = trackpointCount
        self.trackpoints     = []
    
    def __getitem__(self, attr):
        return getattr(self, attr)
    
    def __str__(self):
        return "%02i %s %08i %08i %08i %08i %04i" % (self.id, self.date, self.distance, self.calories, self.topspeed, self.trackpointCount, 0)

    def __hex__(self):
        date = Utilities.dec2hex(self.date.strftime('%y'),2) + Utilities.dec2hex(self.date.strftime('%m'),2) + \
               Utilities.dec2hex(self.date.strftime('%d'),2) + Utilities.dec2hex(self.date.strftime('%H'),2) + \
               Utilities.dec2hex(self.date.strftime('%M'),2) + Utilities.dec2hex(self.date.strftime('%S'),2)
               
        infos = Utilities.dec2hex(self.duration,8) + Utilities.dec2hex(self.distance,8) + \
                Utilities.dec2hex(self.calories,4) + Utilities.dec2hex(self.topspeed,4) + \
                Utilities.dec2hex(self.trackpointCount,8)
        
        #package segments of 136 trackpoints
        chunks = []
        for frome in xrange(0, self.trackpointCount, 136):
            to = (self.trackpointCount - 1) if (frome + 135 > self.trackpointCount) else (frome + 135)
            
            trackpointsConverted = ''.join([hex(trackpoint) for trackpoint in self.trackpoints[frome:to+1]])
            #first segments uses 90, all following 91
            isFirst = '90' if frome == 0 else '91'
            payload = Utilities.dec2hex(27 + (15 * ((to-frome) + 1)), 4)                      
            checksum = Utilities.checkersum((GH600.COMMANDS['setTracks'] % {'payload':payload, 'isFirst':isFirst, 'trackInfo':date+infos, 'from':Utilities.dec2hex(frome,4), 'to':Utilities.dec2hex(to,4), 'trackpoints': trackpointsConverted, 'checksum':'00'})[2:-2])
                       
            chunks.append(GH600.COMMANDS['setTracks'] % {'payload':payload, 'isFirst':isFirst, 'trackInfo':date+infos, 'from':Utilities.dec2hex(frome,4), 'to':Utilities.dec2hex(to,4), 'trackpoints': trackpointsConverted, 'checksum':checksum})
        return ''.join(chunks)
        
    def fromHex(self, hex, timezone=pytz.utc):
        if len(hex) == 44 or len(hex) == 48:
            self.date            = datetime.datetime(2000+Utilities.hex2dec(hex[0:2]), Utilities.hex2dec(hex[2:4]), Utilities.hex2dec(hex[4:6]), Utilities.hex2dec(hex[6:8]), Utilities.hex2dec(hex[8:10]), Utilities.hex2dec(hex[10:12]), tzinfo=timezone)
            self.duration        = datetime.timedelta(seconds=Utilities.hex2dec(hex[12:20]))
            self.distance        = Utilities.hex2dec(hex[20:28])
            self.calories        = Utilities.hex2dec(hex[28:32])
            self.topspeed        = Utilities.hex2dec(hex[32:36])
            self.trackpointCount = Utilities.hex2dec(hex[36:44])
                
            if len(hex) == 48:
                self.id = Utilities.hex2dec(hex[44:48])
            return self
        else:
            raise GH600ParseException(self.__class__.__name__, len(hex), 44)
        
    def addTrackpointsFromHex(self, hex):        
        trackpoints = Utilities.chop(hex, 30)
        for trackpoint in trackpoints: 
            parsedTrackpoint = Trackpoint().fromHex(trackpoint)
            
            if not self.trackpoints:
                parsedTrackpoint.calculateDate(self.date)
            else:
                parsedTrackpoint.calculateDate(self.trackpoints[-1].date)
            self.trackpoints.append(parsedTrackpoint)
                                        
    def export(self, format, **kwargs):
        ef = ExportFormat(format)
        ef.exportTrack(self)
