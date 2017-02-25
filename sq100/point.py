class Point(object):

    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return "(%s, %s)" % (self.latitude, self.longitude)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
