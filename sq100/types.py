import datetime


class CoordinateBounds(object):

    def __init__(self, minimum, maximum):
        self.min = minimum
        self.max = maximum

    def __str__(self):
        return "(%s, %s)" % (self.min, self.max)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Lap(object):

    def __init__(self,
                 duration=None,
                 total_time=None,
                 distance=None,
                 calories=None,
                 max_speed=None,
                 max_heart_rate=None,
                 avg_heart_rate=None,
                 min_height=None,
                 max_height=None,
                 first_index=None,
                 last_index=None):
        self.duration = duration
        self.total_time = total_time
        self.distance = distance
        self.calories = calories
        self.max_speed = max_speed
        self.max_heart_rate = max_heart_rate
        self.avg_heart_rate = avg_heart_rate
        self.min_height = min_height
        self.max_height = max_height
        self.first_index = first_index
        self.last_index = last_index

#     def calculateDate(self, date):
#         self.end = date + datetime.timedelta(
#             milliseconds = (self.__until * 100))
#         self.start = self.end - datetime.timedelta(
#             milliseconds = (self.__elapsed * 100))
#         self.duration = self.end - self.start
#
#     def calculateCoordinates(self, trackpoints):
#         relative_to_start = relative_to_end = {}
#
#         for trackpoint in trackpoints:
#             relative_to_start[abs(self.start - trackpoint.date)] = trackpoint
#             relative_to_end[abs(self.end - trackpoint.date)] = trackpoint
#
#         nearest_start_point = relative_to_start[min(relative_to_start)]
#         nearest_end_point = relative_to_end[min(relative_to_end)]
#
#         self.startPoint = Point(nearest_start_point.latitude,
#                                 nearest_start_point.longitude)
#         self.endPoint = Point(nearest_end_point.latitude,
#                               nearest_end_point.longitude)


class Point(object):

    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return "(%s, %s)" % (self.latitude, self.longitude)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Track(object):

    def __init__(self,
                 ascending_height=None,
                 avg_heart_rate=None,
                 calories=None,
                 date=None,
                 descending_height=None,
                 description=None,
                 distance=None,
                 duration=None,
                 laps=[],
                 max_heart_rate=None,
                 max_height=None,
                 max_speed=None,
                 memory_block_index=None,
                 min_height=None,
                 name=None,
                 no_laps=None,
                 no_track_points=None,
                 track_id=None,
                 track_points=[]
                 ):
        self.ascending_height = ascending_height
        self.avg_heart_rate = avg_heart_rate
        self.calories = calories
        self.date = date
        self.descending_height = descending_height
        self.description = description
        self.distance = distance
        self.duration = duration
        self.id = track_id
        self.max_heart_rate = max_heart_rate
        self.max_height = max_height
        self.max_speed = max_speed
        self.memory_block_index = memory_block_index
        self.min_height = min_height
        self.name = name
        self.no_laps = no_laps
        self.no_track_points = no_track_points
        self.track_points = track_points
        self.laps = laps

    def bounds(self):
        raise NotImplementedError

    def compatible_to(self, other):
        def c(a, b):
            return a is None or b is None or a == b
        return (
            c(self.ascending_height, other.ascending_height) and
            c(self.avg_heart_rate, other.avg_heart_rate) and
            c(self.calories, other.calories) and
            c(self.date, other.date) and
            c(self.descending_height, other.descending_height) and
            c(self.distance, other.distance) and
            c(self.duration, other.duration) and
            c(self.id, other.id) and
            c(self.max_heart_rate, other.max_heart_rate) and
            c(self.max_height, other.max_height) and
            c(self.max_speed, other.max_speed) and
            c(self.memory_block_index, other.memory_block_index) and
            c(self.min_height, other.min_height) and
            c(self.no_laps, other.no_laps) and
            c(self.no_track_points, other.no_track_points))

    def complete(self):
        return len(self.track_points) == self.no_track_points

    def update_track_point_times(self):
        interval = datetime.timedelta(0)
        for tp in self.track_points:
            interval += tp.interval
            tp.time = self.date + interval


class TrackPoint(Point):

    def __init__(self,
                 latitude=None,
                 longitude=None,
                 altitude=None,
                 speed=None,
                 heart_rate=None,
                 interval=None,
                 date=None):
        Point.__init__(self, latitude=latitude, longitude=longitude)
        self.altitude = altitude
        self.speed = speed
        self.heart_rate = heart_rate
        self.interval = interval
        self.date = date
        Point.__init__(self, latitude, longitude)
