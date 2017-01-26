
class Track(object):    
    def __init__(self,
                 ascending_height=None,
                 avg_heart_rate=None,
                 calories=None,
                 date=None, 
                 descending_height=None,
                 distance=None, 
                 duration=None, 
                 lap_count=None,
                 max_heart_rate=None,
                 max_height=None,
                 max_speed=None, 
                 memory_block_index=None,
                 min_height=None,
                 track_id=None,
                 trackpoint_count=None, 
                 ):
        self.ascending_height = ascending_height
        self.avg_heart_rate = avg_heart_rate
        self.calories = calories
        self.date = date
        self.descending_height = descending_height
        self.distance = distance
        self.duration = duration
        self.id = track_id
        self.lap_count = lap_count
        self.max_heart_rate = max_heart_rate
        self.max_height = max_height
        self.max_speed = max_speed
        self.memory_block_index = memory_block_index
        self.min_height = min_height
        self.trackpoint_count = trackpoint_count
        self.trackpoints = []
