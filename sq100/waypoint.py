from sq100.point import Point


class Waypoint(Point):
    TYPES = {
        0:  'DOT',
        1:  'HOUSE',
        2:  'TRIANGLE',
        3:  'TUNNEL',
        4:  'CROSS',
        5:  'FISH',
        6:  'LIGHT',
        7:  'CAR',
        8:  'COMM',
        9:  'REDCROSS',
        10: 'TREE',
        11: 'BUS',
        12: 'COPCAR',
        13: 'TREES',
        14: 'RESTAURANT',
        15: 'SEVEN',
        16: 'PARKING',
        17: 'REPAIRS',
        18: 'MAIL',
        19: 'DOLLAR',
        20: 'GOVOFFICE',
        21: 'CHURCH',
        22: 'GROCERY',
        23: 'HEART',
        24: 'BOOK',
        25: 'GAS',
        26: 'GRILL',
        27: 'LOOKOUT',
        28: 'FLAG',
        29: 'PLANE',
        30: 'BIRD',
        31: 'DAWN',
        32: 'RESTROOM',
        33: 'WTF',
        34: 'MANTARAY',
        35: 'INFORMATION',
        36: 'BLANK'
    }

    def __init__(self, latitude=0, longitude=0, altitude=0, title='', type=0):
        self.altitude = altitude
        self.title = title
        self.type = type
        super(Waypoint, self).__init__(latitude, longitude)

    def __str__(self):
        return "%s (%f,%f)" % (self.title, self.latitude, self.longitude)
