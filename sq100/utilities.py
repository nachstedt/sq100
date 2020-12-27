import os
import sys


class Utilities():
    @classmethod
    def dec2hex(self, n, pad = False):
        hex = "%X" % int(n)
        if pad:
            hex = hex.rjust(pad, '0')[:pad]
        return hex
    
    @classmethod
    def hex2dec(self, hex):
        return int(hex, 16)
    
    @classmethod
    def hex2signedDec(self, hex):
        value = self.hex2dec(hex)
        if value > 32767:
            value = value - 32767 - 2
        return int(value)
    
    @classmethod
    def hex2chr(self, hex):
        out = ''
        for i in range(0,len(hex),2):
            out += chr(self.hex2dec(hex[i:i+2]))
        return out
    
    @classmethod
    def chr2hex(self, chr):
        out = ''
        for i in range(0,len(chr)):
            out += '%(#)02X' % {"#": ord(chr[i])}
        return out
    
    @classmethod
    def coord2hex(self, coord):
        '''takes care of negative coordinates'''
        coord = Decimal(str(coord))
        
        if coord < 0:
            return self.dec2hex((coord * Decimal(1000000) + Decimal(4294967295)),8)
        else:
            return self.dec2hex(coord * Decimal(1000000),8)
    
    @classmethod
    def hex2coord(self, hex):
        '''takes care of negative coordinates'''
        if hex[0:1] == 'F':
            return Decimal(self.hex2dec(hex)/Decimal(1000000)) - Decimal('4294.967295')
        else:
            return Decimal(self.hex2dec(hex)/Decimal(1000000))
    
    @classmethod
    def chop(self, s, chunk):
        return [s[i*chunk:(i+1)*chunk] for i in range((len(s)+chunk-1)//chunk)]
    
    @classmethod 
    def checkersum(self, hex):
        checksum = 0
        
        for i in range(0,len(hex),2):
            checksum = checksum^int(hex[i:i+2],16)
        return self.dec2hex(checksum)
    
    @classmethod 
    def getAppPrefix(self, *args):
        ''' Return the location the app is running from'''
        isFrozen = False
        try:
            isFrozen = sys.frozen
        except AttributeError:
            pass
        if isFrozen:
            appPrefix = os.path.split(sys.executable)[0]
        else:
            appPrefix = os.path.split(os.path.abspath(sys.argv[0]))[0]
        if args:
            appPrefix = os.path.join(appPrefix,*args)
        return appPrefix
