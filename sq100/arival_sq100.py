import collections
import datetime
import logging
import struct

from sq100.serial_connection import SerialConnection
from sq100.track_with_laps import TrackWithLaps

logger = logging.getLogger(__name__)


class ArivalSQ100(object):

    def __init__(self):
        self.serial = SerialConnection()
    
    def connect(self):
        self.serial.connect()
    
    def disconnect(self):
        self.serial.disconnect()
    
    def tracklist(self):
        command = b'\x02\x00\x01\x78\x79'
        data = self.serial.query(command)
        payload_length, = struct.unpack(">H", data[1:3])
        number_tracks = payload_length//29 
        logger.info('%i tracks found' % number_tracks)
        TrackHeader = collections.namedtuple('TrackHeader', [
            'year', 'month', 'day', 'hour', 'minute', 'second', 'total_points', 
            'total_time', 'distance', 'lap_count', 'unused_1', 'id', 
            'unused_2'])
        track_headers = map(
            TrackHeader._make, 
            struct.iter_unpack(">6B3IH7s2B", data[3:-1]))
        tracks = [TrackWithLaps(
                    date=datetime.datetime(
                        2000+t.year, t.month, t.day, t.hour, t.minute, t.second),
                    lapCount=t.lap_count,
                    duration=datetime.timedelta(seconds=t.total_time/10),
                    distance=t.distance,
                    trackpointCount=t.total_points,
                    id=t.id)
                  for t in track_headers]
        return tracks