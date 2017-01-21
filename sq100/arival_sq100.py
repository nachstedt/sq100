import collections
import functools
import datetime
import logging
import struct

from sq100.exceptions import SQ100MessageException
from sq100.track_with_laps import TrackWithLaps

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
            'total_time', 'distance', 'lap_count', 'unused_1', 'id', 
            'unused_2'])
        track_headers = map(
            TrackHeader._make, 
            struct.iter_unpack(">6B3IH7s2B", msg.parameter))
        tracks = [
            TrackWithLaps(
                date=datetime.datetime(
                    2000+t.year, t.month, t.day, t.hour, t.minute, t.second),
                lapCount=t.lap_count,
                duration=datetime.timedelta(seconds=t.total_time/10),
                distance=t.distance,
                trackpointCount=t.total_points,
                id=t.id)
            for t in track_headers]
        return tracks