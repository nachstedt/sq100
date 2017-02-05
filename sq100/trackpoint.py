from sq100.point import Point


class Trackpoint(Point):

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
        super(Trackpoint, self).__init__(latitude, longitude)
