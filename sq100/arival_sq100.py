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
            'command', 'payload_length', 'parameter', 'checksum'])
        msg = Message._make(struct.unpack(">BH%dsB" % (len(message)-4), message))
        if msg.payload_length != len(msg.parameter):
            raise SQ100MessageException("paylod has wrong length")
        if msg.checksum != ArivalSQ100._calc_checksum(msg.parameter):
            raise SQ100MessageException("checksum wrong")
        return msg
    
    @staticmethod
    def _process_track_info_parameter(parameter):
        TrackHeader = collections.namedtuple('TrackHeader', [
            'year', 'month', 'day', 'hour', 'minute', 'second', 
            'no_points', 'duration', 'distance', 
            'no_laps', 'NA_1', 'memory_block_index', 'NA_2', 'id', 
            'msg_type'])
        header = TrackHeader._make(
            struct.unpack(">6B3I5HB", parameter[:29]))
        TrackInfo = collections.namedtuple('TrackInfo', [
            'calories', 'NA_1', 'max_speed', 'max_heart_rate', 'avg_heart_rate',
            'asc_height', 'des_height', 'min_height', 'max_height',
            'NA_2'])
        info = TrackInfo._make(
            struct.unpack(">3H2B4H13s", parameter[29:]))
        track = Track(
            date=datetime.datetime(
                2000+header.year, header.month, header.day, 
                header.hour, header.minute, header.second),
            trackpoint_count=header.no_points,
            duration=datetime.timedelta(seconds=header.duration/10),            
            distance=header.distance,
            lap_count=header.no_laps,
            memory_block_index=header.memory_block_index,
            track_id=header.id,
            calories=info.calories,
            max_speed=info.max_speed,
            max_heart_rate=info.max_heart_rate,
            avg_heart_rate=info.avg_heart_rate,
            ascending_height=info.asc_height,
            descending_height=info.des_height,
            min_height=info.min_height,
            max_height=info.max_height)
        return track
    
    @staticmethod
    def _process_lap_info_parameter(parameter, track):
        TrackHeader = collections.namedtuple('TrackHeader', [
            'year', 'month', 'day', 'hour', 'minute', 'second', 
            'no_points', 'duration', 'distance', 
            'no_laps', 'NA_1', 'msg_type'])
        header = TrackHeader._make(
            struct.unpack(">6B3IH8sB", parameter[:29]))
        LapInfo = collections.namedtuple('LapInfo', [
            'accrued_time', 'total_time', 'distance', 'calories',
            'NA_1', 'max_speed', 'max_hr', 'avg_hr', 'min_height',
            'max_height', 'NA_2', 'first_index', 'last_index'])
        laps = map(
            LapInfo._make, 
            struct.iter_unpack(">3I3H2B2H13s2H", parameter[29:]))
        for lap in laps:
            track.add_lap(lap)

    @staticmethod
    def _process_trackpoint_parameter(parameter, track):
        TrackHeader = collections.namedtuple('TrackHeader', [
            'year', 'month', 'day', 'hour', 'minute', 'second', 
            'no_points', 'duration', 'distance', 
            'no_laps', 'first_session_index', 'last_session_index',
            'msg_type'])
        header = TrackHeader._make(
            struct.unpack(">6B3IH2IB", parameter[:29]))
        TrackPointData = collections.namedtuple('TrackPointData', [
            'latitude', 'longitude', 'altitude', 'NA_1', 'speed', 
            'heart_rate', 'NA_2', 'interval_time', 'NA_3'])
        trackpoints = map(
            TrackPointData._make,
            struct.iter_unpack('>2i3HBHH6s', parameter[29:]))
        for tp in trackpoints:
            track.add_trackpoint(tp)

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
            'year', 'month', 'day', 'hour', 'minute', 'second', 
            'no_points', 'duration', 'distance', 
            'lap_count', 'unused_1', 'memory_block_index', 'unused_2', 'id', 
            'unused_3'])
        track_headers = map(
            TrackHeader._make, 
            struct.iter_unpack(">6B3I5HB", msg.parameter))
        tracks = [
            Track(
                date=datetime.datetime(
                    2000+t.year, t.month, t.day, t.hour, t.minute, t.second),
                lap_count=t.lap_count,
                duration=datetime.timedelta(seconds=t.duration/10),
                distance=t.distance,
                trackpoint_count=t.no_points,
                memory_block_index=t.memory_block_index,
                track_id=t.id)
            for t in track_headers]
        return tracks
    
    def get_tracks(self, memory_indices):        
        no_tracks = len(memory_indices)
        params = struct.pack(">H%dH" % no_tracks, no_tracks, *memory_indices)
        msg = self._query(0x80, params)
        track = None
        tracks = []
        while msg.command != 0x8a:
            msg_type = msg.parameter[28]
            if msg_type == 0:
                track = self._process_track_info_parameter(msg.parameter)
            elif msg_type == 0xAA:
                self._process_lap_info_parameter(msg.parameter, track)
            elif msg_type == 0x55:
                self._process_trackpoint_parameter(msg.parameter, track)
                if track.complete():
                    tracks.append(track)
                    track = None
            msg = self._query(0x81)
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
        