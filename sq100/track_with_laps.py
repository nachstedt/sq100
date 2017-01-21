from sq100.exceptions import GH600ParseException
from sq100.track import Track

import datetime
import pytz


class TrackWithLaps(Track):
    def __init__(self, date = datetime.datetime.utcnow(), duration = 0, distance = 0, calories = 0, topspeed = 0, trackpointCount = 0, lapCount = 0, id=0):
        self.lapCount = lapCount
        self.laps = []
        super(TrackWithLaps, self).__init__(date, duration,distance, calories, topspeed, trackpointCount, id)
    
    def __str__(self):
        return "%02i %s %08i %08i %08i %08i %04i" % (self.id, self.date, self.distance, self.calories, self.topspeed, self.trackpointCount, self.lapCount)
    
    def __hex__(self):            
        date = Utilities.dec2hex(self.date.strftime('%y'),2) + Utilities.dec2hex(self.date.strftime('%m'),2) + \
               Utilities.dec2hex(self.date.strftime('%d'),2) + Utilities.dec2hex(self.date.strftime('%H'),2) + \
               Utilities.dec2hex(self.date.strftime('%M'),2) + Utilities.dec2hex(self.date.strftime('%S'),2)
               
        infos = Utilities.dec2hex(self.lapCount,2) + Utilities.dec2hex(self.duration,8) + \
                Utilities.dec2hex(self.distance,8) + Utilities.dec2hex(self.calories,4) + Utilities.dec2hex(self.topspeed,4) + \
                Utilities.dec2hex(0,8) + Utilities.dec2hex(self.trackpointCount,8)
                
        lapsConverted = Utilities.dec2hex(0,44)
        payload_laps = Utilities.dec2hex(32 + (self.lapCount * 22),4)
        checksum_laps = Utilities.checkersum((GH625.COMMANDS['setTracksLaps'] % {'payload':payload_laps, 'trackInfo':date+infos, 'laps': lapsConverted, 'nrOfTrackpoints': Utilities.dec2hex(self.trackpointCount,8), 'checksum':'00'})[2:-2])
        lap_chunk = GH625.COMMANDS['setTracksLaps'] % {'payload':payload_laps, 'trackInfo':date+infos, 'laps': lapsConverted, 'nrOfTrackpoints': Utilities.dec2hex(self.trackpointCount,8), 'checksum':checksum_laps}

        chunks = []
        chunks.append(lap_chunk)
        #package segments of 136 trackpoints
        for frome in xrange(0, self.trackpointCount, 136):
            to = (self.trackpointCount - 1) if (frome + 135 > self.trackpointCount) else (frome + 135)
            
            trackpointsConverted = ''.join([hex(trackpoint) for trackpoint in self.trackpoints[frome:to+1]])
            payload = Utilities.dec2hex(32 + (15 * ((to-frome) + 1)), 4)                      
            checksum = Utilities.checkersum((GH625.COMMANDS['setTracks'] % {'payload':payload, 'trackInfo':date+infos, 'from':Utilities.dec2hex(frome,4), 'to':Utilities.dec2hex(to,4), 'trackpoints': trackpointsConverted, 'checksum':'00'})[2:-2])
                       
            chunks.append(GH625.COMMANDS['setTracks'] % {'payload':payload, 'trackInfo':date+infos, 'from':Utilities.dec2hex(frome,4), 'to':Utilities.dec2hex(to,4), 'trackpoints': trackpointsConverted, 'checksum':checksum})
        return ''.join(chunks)
    
    def fromHex(self, hex, timezone=pytz.utc):
        if len(hex) == 58 or len(hex) == 62:            
            self.date            = datetime.datetime(2000+Utilities.hex2dec(hex[0:2]), Utilities.hex2dec(hex[2:4]), Utilities.hex2dec(hex[4:6]), Utilities.hex2dec(hex[6:8]), Utilities.hex2dec(hex[8:10]), Utilities.hex2dec(hex[10:12]), tzinfo=timezone)
            self.lapCount        = Utilities.hex2dec(hex[12:14])
            self.duration        = datetime.timedelta(Utilities.hex2dec(hex[14:22]))
            self.distance        = Utilities.hex2dec(hex[22:30])
            self.calories        = Utilities.hex2dec(hex[30:34])
            self.topspeed        = Utilities.hex2dec(hex[34:38])
            #self.unknown        = Utilities.hex2dec(hex[38:42])
            #self.trackpointCount = Utilities.hex2dec(hex[42:50])
            self.trackpointCount = Utilities.hex2dec(hex[50:54])
            #self.unknown2       = Utilities.hex2dec(hex[50:54])
            #self.number         = Utilities.hex2dec(hex[58:62])
                
            if len(hex) == 62:
                self.id = Utilities.hex2dec(hex[54:58])
                #self.id = Utilities.hex2dec(hex[58:62])
            return self
        else:
            raise GH600ParseException(self.__class__.__name__, len(hex), 58)
        
    def addLapsFromHex(self, hex):
        laps = Utilities.chop(hex,44)
        for lap in laps: 
            parsedLap = Lap().fromHex(lap)
            parsedLap.calculateDate(self.date)
            self.laps.append(parsedLap)
