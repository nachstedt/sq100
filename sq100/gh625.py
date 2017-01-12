from gh600 import GH600
from serial_required import serial_required
from track_with_laps import TrackWithLaps
from utilities import Utilities

import collections
import datetime
import struct
import time


class GH625(GH600):
    GH600.COMMANDS.update({
       'setTracks':     '02%(payload)s91%(trackInfo)s%(from)s%(to)s%(trackpoints)s%(checksum)s',
       'setTracksLaps': '02%(payload)s90%(trackInfo)s%(laps)s%(nrOfTrackpoints)s%(checksum)s'
    })
    
    @serial_required
    def getTracklist(self):
        tracklist = self._querySerial('getTracklist')

        payload_length, = struct.unpack(">H", tracklist[1:3])
        number_tracks = payload_length//29 
        self.logger.info('%i tracks found' % number_tracks)
        
        TrackHeader = collections.namedtuple('TrackHeader', [
            'year', 'month', 'day', 'hour', 'minute', 'second', 'total_points', 
            'total_time', 'distance', 'lap_count', 'unused_1', 'id', 'unused_2'])
        
        return [
            TrackWithLaps(
                date=datetime.datetime(2000+track.year, track.month, track.day,
                                       track.hour, track.minute, track.second),
                lapCount=track.lap_count,
                duration=datetime.timedelta(seconds=track.total_time/10),
                distance=track.distance,
                trackpointCount=track.total_points,
                id=track.id)
            for track in map(
                TrackHeader._make, 
                 struct.iter_unpack(">6B3IH7s2B", tracklist[3:-1]))]
        
    @serial_required
    def getTracks(self, trackIds):
        trackIds = [Utilities.dec2hex(str(id), 4) for id in trackIds]
        payload = Utilities.dec2hex((len(trackIds) * 512) + 896, 4)
        numberOfTracks = Utilities.dec2hex(len(trackIds), 4) 
        checksum = Utilities.checkersum("%s%s%s" % (payload, numberOfTracks, ''.join(trackIds)))
        self._writeSerial('getTracks', **{'payload':payload, 'numberOfTracks':numberOfTracks, 'trackIds':''.join(trackIds), 'checksum':checksum})
                    
        tracks = []
        last = -1
        initializeNewTrack = True
        
        while True:
            data = self._readSerial(2075)
            time.sleep(2)
            
            if data != '8A000000':
                #shoud new track be initialized?
                if initializeNewTrack:
                    self.logger.debug('initalizing new track')
                    track = TrackWithLaps().fromHex(data[6:64], self.timezone)
                    initializeNewTrack = False
                
                if data[60:64] == "FFFF":
                    self.logger.debug('adding laps')
                    track.addLapsFromHex(data[68:-2])
                    self._writeSerial('requestNextTrackSegment')
                
                elif Utilities.hex2dec(data[60:64]) == last + 1:
                    self.logger.debug('adding trackpoints %i-%i of %i' % (Utilities.hex2dec(data[60:64]), Utilities.hex2dec(data[64:68]), track.trackpointCount))
                    track.addTrackpointsFromHex(data[68:-2])
                    last = Utilities.hex2dec(data[64:68])
                    #check if last segment of track     
                    if last + 1 == track.trackpointCount:
                        tracks.append(track)
                        last = -1
                        initializeNewTrack = True
                    self._writeSerial('requestNextTrackSegment')
                
                else:
                    #re-request last segment again
                    self.logger.debug('last segment Errornous, re-requesting')
                    self.serial.flushInput()
                    self._writeSerial('requestErrornousTrackSegment')
            else:
                #we are done, do maintenance work here
                for track in tracks:
                    for lap in track.laps:
                        lap.calculateCoordinates(track.trackpoints)
                break        

        self.logger.info('number of tracks %d' % len(tracks))
        return tracks
    
    @serial_required
    def setTracks(self, tracks):        
        for track in tracks:
            lapChunk = hex(track)[:72 + (track.lapCount * 44)]
            
            response = self._querySerial(lapChunk)
            if response == '91000000' or response == '90000000':
                self.logger.info('uploaded lap information of track successfully')
            else:
                raise GH600Exception

            trackpointChunks = Utilities.chop(hex(track)[len(lapChunk):], 4152)
            for i, chunk in enumerate(trackpointChunks):
                response = self._querySerial(chunk)

                if response == '9A000000':
                    self.logger.info('successfully uploaded track')
                elif response == '91000000' or response == '90000000':
                    self.logger.debug("uploaded chunk %i of %i" % (i+1, len(trackpointChunks)))
                elif response == '92000000':
                    #this probably means segment was not as expected, resend previous segment?
                    self.logger.debug('wtf')
                else:
                    #print response
                    self.logger.info('error uploading track')
                    raise GH600Exception
        return len(tracks)
