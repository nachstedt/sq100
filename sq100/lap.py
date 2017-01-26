class Lap(object):
    def __init__(self, 
                 accrued_time=None,
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
        self.accrued_time = accrued_time
        self.total_time = total_time
        self.distance = distance
        self.calories = calories
        self.max_speed = max_speed
        self.max_heart_rate = max_heart_rate
        self.avg_herat_rate = avg_heart_rate
        self.min_height = min_height
        self.max_height = max_height
        self.first_index = first_index
        self.last_index = last_index

#     def calculateDate(self, date):
#         self.end = date + datetime.timedelta(milliseconds = (self.__until * 100))
#         self.start = self.end - datetime.timedelta(milliseconds = (self.__elapsed * 100))
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
#         self.startPoint = Point(nearest_start_point.latitude, nearest_start_point.longitude)
#         self.endPoint = Point(nearest_end_point.latitude, nearest_end_point.longitude)
