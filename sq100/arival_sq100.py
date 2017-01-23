import collections
import functools
import datetime
import logging
import struct

from sq100.exceptions import SQ100MessageException
from sq100.track import Track

logger = logging.getLogger(__name__)


class ArivalSQ100(object):

    def __init__(self, serial):
        self.serial = serial

    @staticmethod
    def _calc_checksum(payload):
        payload_len = struct.pack("H", len(payload))
        checksum=functools.reduce(lambda x,y:x^y, payload_len+payload)
        return checksum
    
    @staticmethod
    def _create_message(command, parameter=b''):
        start_sequence=0x02
        payload=bytes([command])+parameter
        payload_length=len(payload)
        checksum = ArivalSQ100._calc_checksum(payload)
        return struct.pack(">BH%dsB" % len(payload), 
                           start_sequence, payload_length, payload, checksum)
    
    @staticmethod
    def _unpack_message(message):
        Message = collections.namedtuple("Message", [
            'device_command', 'payload_length', 'parameter', 'checksum'])
        msg = Message._make(struct.unpack(">BH%dsB" % (len(message)-4), message))
        if msg.payload_length != len(msg.parameter):
            raise SQ100MessageException("paylod has wrong length")
        if msg.checksum != ArivalSQ100._calc_checksum(msg.parameter):
            raise SQ100MessageException("checksum wrong")
        return msg
    
    def _query(self, command, parameter=b''):
        return self._unpack_message(
            self.serial.query(
                self._create_message(command, parameter)))
    
    def connect(self):
        self.serial.connect()
    
    def disconnect(self):
        self.serial.disconnect()
    
    def tracklist(self):
        msg = self._query(0x78)
        number_tracks = msg.payload_length//29 
        logger.info('%i tracks found' % number_tracks)
        TrackHeader = collections.namedtuple('TrackHeader', [
            'year', 'month', 'day', 'hour', 'minute', 'second', 'total_points', 
            'total_time', 'distance', 'lap_count', 'unused_1', 
            'memory_block_index', 'unused_2', 'id', 'unused_3'])
        track_headers = map(
            TrackHeader._make, 
            struct.iter_unpack(">6B3I5HB", msg.parameter))
        tracks = [
            Track(
                date=datetime.datetime(
                    2000+t.year, t.month, t.day, t.hour, t.minute, t.second),
                lap_count=t.lap_count,
                duration=datetime.timedelta(seconds=t.total_time/10),
                distance=t.distance,
                trackpoint_count=t.total_points,
                memory_block_index=t.memory_block_index,
                track_id=t.id)
            for t in track_headers]
        return tracks
    
    def get_tracks(self, track_ids):
#         trackIds = [Utilities.dec2hex(str(id), 4) for id in trackIds]
#         payload = Utilities.dec2hex((len(trackIds) * 512) + 896, 4)
#         numberOfTracks = Utilities.dec2hex(len(trackIds), 4) 
#         checksum = Utilities.checkersum("%s%s%s" % (payload, numberOfTracks, ''.join(trackIds)))
#         self._writeSerial('getTracks', **{'payload':payload, 'numberOfTracks':numberOfTracks, 'trackIds':''.join(trackIds), 'checksum':checksum})
        
        no_tracks = len(track_ids)
        msg = self._query(0x80, struct.pack(">H%dH" % no_tracks, no_tracks, *track_ids))
        print(msg)
        msg = self._query(0x81)
        print(msg)
        msg = self._query(0x81)
        print(msg)
        msg = self._query(0x81)
        print(msg)
        return
        
                    
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
        