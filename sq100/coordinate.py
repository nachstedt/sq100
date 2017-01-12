

class Coordinate(Decimal):     
    def __hex__(self):
        return Utilities.coord2hex(Decimal(self))
    
    def fromHex(self, hex):
        if len(hex) == 8:
            #TODO: whack, but works
            self = Coordinate(Utilities.hex2coord(hex))
            return self
        else:
            raise GH600ParseException(self.__class__.__name__, len(hex), 8)
