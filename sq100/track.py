import datetime


class Track(object):    
    def __init__(self, 
                 date = datetime.datetime.utcnow(), 
                 duration = datetime.timedelta(), 
                 distance = 0, 
                 calories = 0,
                 lap_count = 0, 
                 topspeed = 0, 
                 trackpoint_count = 0, 
                 memory_block_index=0,
                 track_id=0):
        self.id = track_id
        self.date = date
        self.duration = duration
        self.distance = distance
        self.calories = calories
        self.lap_count = lap_count
        self.memory_block_index = memory_block_index
        self.topspeed = topspeed
        self.trackpoint_count = trackpoint_count
        self.trackpoints = []
