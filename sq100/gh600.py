

# from __future__ import with_statement
# import os, sys, glob
# 
# import math
# import time, datetime
# import configparser
# import logging
# from decimal import Decimal
# 
# import serial
# from pytz import timezone, utc
# 
# from templates import Template
# from gpxParser import GPXParser
# 
# # new imports
# import struct
# import collections

from gh600_serial_exception import GH600SerialException
from serial_interface import SerialInterface
from serial_required import serial_required
from utilities import Utilities

import configparser
import logging
import pytz


class GH600(SerialInterface):
    """api for Globalsat GH600"""
    
    COMMANDS = {
        'getTracklist'                    : '0200017879',
        #'setTracks'                       : '02%(payload)s%(isFirst)s%(trackInfo)s%(from)s%(to)s%(trackpoints)s%(checksum)s', 
        'getTracks'                       : '0200%(payload)s%(numberOfTracks)s%(trackIds)s%(checksum)s', 
        'requestNextTrackSegment'         : '0200018180', 
        'requestErrornousTrackSegment'    : '0200018283',
        'formatTracks'                    : '0200037900641E',
        'getWaypoints'                    : '0200017776',
        'setWaypoints'                    : '02%(payload)s76%(numberOfWaypoints)s%(waypoints)s%(checksum)s',
        'formatWaypoints'                 : '02000375006412',
        'unitInformation'                 : '0200018584',
        'whoAmI'                          : '020001BFBE',
        'unknown'                         : '0200018382'
    }
            
    def __init__(self):
        self.config = configparser.SafeConfigParser()
        self.config.read(Utilities.getAppPrefix('config.ini'))
        
        self.timezone = pytz.timezone(self.config.get('general', 'timezone'))             
                
        #logging http://www.tiawichiresearch.com/?p=31 / http://www.red-dove.com/python_logging.html
        handler = logging.FileHandler(Utilities.getAppPrefix('GH600.log'))        
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(lineno)d %(funcName)s %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        
        self.logger = logging.getLogger('GH600')
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
                                    
        outputHandler = logging.StreamHandler()
        if self.config.getboolean("debug", "output"):
            level = logging.DEBUG
            format = '%(levelname)s %(funcName)s(%(lineno)d): %(message)s'
        else:
            level = logging.INFO
            format = '%(message)s'
        outputHandler.setFormatter(logging.Formatter(format))
        outputHandler.setLevel(level)
        self.logger.addHandler(outputHandler)
            
        if self.__class__ is GH600:
            if self.config.has_option("general", "firmware"):
                product = {1:'GH-615', 2:'GH-625'}[self.config.getint("general", "firmware")]
            else:
                product = self.getProductModel()
            
            #downcasting to a specific model
            if product == "GH-615":
                from gh615 import GH615
                self.__class__ = GH615
            elif product == "GH-625":
                from gh625 import GH625
                self.__class__ = GH625
        
    @serial_required
    def getProductModel(self):
        try:
            response = self._querySerial('whoAmI')
            watch = Utilities.hex2chr(response[6:-4])
            product, model = watch[:-1], watch[-1:]
            return product
        except GH600SerialException: #no response received, assuming command was not understood => old firmware
            return "GH-615"
        
    @serial_required
    def testConnectivity(self):
        try:
            self._querySerial('whoAmI')
            return True
        except:
            return False
                                           
    def getExportFormats(self):
        formats = []
        
        for format in glob.glob(Utilities.getAppPrefix("exportTemplates", "*.txt")):
            (filepath, filename) = os.path.split(format)
            (shortname, extension) = os.path.splitext(filename)
            e = ExportFormat(shortname)
            formats.append(e)
        return formats
        
    @serial_required
    def getTracklist(self):
        raise NotImplemented('This is an abstract method, please instantiate a subclass')
    
    def getAllTrackIds(self):
        allTracks = self.getTracklist()
        return [track.id for track in allTracks]
    
    def getAllTracks(self):
        return self.getTracks(self.getAllTrackIds())
    
    @serial_required
    def getTracks(self, trackIds):
        raise NotImplemented('This is an abstract method, please instantiate a subclass')
    
    def exportTracks(self, tracks, format = None, path = None, **kwargs):
        if format is None:
            format = self.config.get("export", "default")
        if path is None:
            path = os.path.abspath(Utilities.getAppPrefix(self.config.get('export', 'path')))
        
        ef = ExportFormat(format)
        ef.exportTracks(tracks, path, **kwargs)
    
    def importTracks(self, files, **kwargs):        
        if "path" in kwargs:
            path = os.path.join(kwargs['path'])
        else:
            path = Utilities.getAppPrefix('import')
        
        tracks = []
        for file in files:
            with open(os.path.join(path,file)) as f:
                data = f.read()
                tracks.extend(self.__parseGpxTrack(data))
        
        self.logger.info('imported tracks %i' % len(tracks))
        return tracks
    
    def __parseGpxTrack(self, track):
        gpx = GPXParser(track)
        return gpx.tracks
    
    @serial_required
    def setTracks(self, tracks):
        raise NotImplemented('This is an abstract method, please instantiate a subclass')

    @serial_required
    def formatTracks(self):
        self._writeSerial('formatTracks')
        #wait long for response
        time.sleep(10)
        response = self._readSerial()
        
        if response == '79000000':
            self.logger.info('format tracks successful')
            return True
        else:
            self.logger.error('format not successful')
            return False
        
    @serial_required
    def getWaypoints(self):
        response = self._querySerial('getWaypoints')            
        waypoints = Utilities.chop(response[6:-2], 36) #trim junk
        return [Waypoint().fromHex(waypoint) for waypoint in waypoints] 

    def exportWaypoints(self, waypoints, **kwargs):
        if 'path' in kwargs:
            filepath = os.path.join(kwargs['path'], 'waypoints.txt')
        else:    
            filepath = Utilities.getAppPrefix('waypoints.txt')
        
        template = Template.from_file(Utilities.getAppPrefix('waypoint_template.txt'))
        rendered = template.render(waypoints = waypoints)

        with open(filepath,'wt') as f:
            f.write(rendered)
            
        self.logger.info('Successfully wrote waypoints to %s' % filepath)
        return filepath
    
    def importWaypoints(self, **kwargs):
        if 'path' in kwargs:
            filepath = os.path.join(kwargs['path'], 'waypoints.txt')
        else:    
            filepath = Utilities.getAppPrefix('waypoints.txt')
                
        with open(filepath) as f:
            importedWaypoints = f.read()
    
        waypoints = []
        for waypoint in eval(importedWaypoints):
            waypoints.append(Waypoint(str(waypoint['latitude']), str(waypoint['longitude']), waypoint['altitude'], waypoint['title'], waypoint['type']))
            
        self.logger.info('Successfully read waypoints %i' % len(waypoints)) 
        return waypoints
    
    @serial_required
    def setWaypoints(self, waypoints):                               
        waypointsConverted = ''.join([hex(waypoint) for waypoint in waypoints])
        numberOfWaypoints = Utilities.dec2hex(len(waypoints), 4)
        payload =  Utilities.dec2hex(3 + (18 * len(waypoints)), 4)
        checksum = Utilities.checkersum("%s76%s%s" % (str(payload), str(numberOfWaypoints), waypointsConverted))
        
        response = self._querySerial('setWaypoints', **{'payload':payload, 'numberOfWaypoints':numberOfWaypoints, 'waypoints': waypointsConverted, 'checksum':checksum})
        
        if response[:8] == '76000200':
            waypointsUpdated = Utilities.hex2dec(response[8:10])
            self.logger.info('waypoints updated: %i' % waypointsUpdated)
            return waypointsUpdated
        else:
            self.logger.error('error uploading waypoints')
            return False

    @serial_required
    def formatWaypoints(self):
        self._writeSerial('formatWaypoints')
        time.sleep(10)
        response = self._readSerial()
        
        if response == '75000000':
            self.logger.info('deleted all waypoints')
            return True
        else:
            self.logger.error('deleting all waypoints failed')
            return False 

    @serial_required
    def getNmea(self):
        #http://regexp.bjoern.org/archives/gps.html
        #looks interesting
        #http://twistedmatrix.com/trac/browser/trunk/twisted/protocols/gps/nmea.py
        def dmmm2dec(degrees,sw):
            deg = math.floor(degrees/100.0) #decimal degrees
            frac = ((degrees/100.0)-deg)/0.6 #decimal fraction
            ret = deg+frac #positive return value
            if ((sw == "S") or (sw == "W")):
                ret=ret*(-1) #flip sign if south or west
            return ret
        
        line = ""
        while not line.startswith("$GPGGA"):
            self.logger.debug("waiting at serialport: %i" % self.serial.inWaiting())
            line = self.serial.readline()
            print(line)
        
        # calculate our lat+long
        tokens = line.split(",")
        lat = dmmm2dec(float(tokens[2]),tokens[3]) #[2] is lat in deg+minutes, [3] is {N|S|W|E}
        lng = dmmm2dec(float(tokens[4]),tokens[5]) #[4] is long in deg+minutes, [5] is {N|S|W|E}
        return lat, lng
    
    @serial_required
    def getUnitInformation(self):
        response = self._querySerial('unitInformation')
                
        if len(response) == 180:
            unit = {
                'device_name'      : Utilities.hex2chr(response[4:20]),
                'version'          : Utilities.hex2dec(response[50:52]),
                #'dont know'       : self.__hex2dec(response[52:56]),
                'firmware'         : Utilities.hex2chr(response[56:88]),
                'name'             : Utilities.hex2chr(response[90:110]),
                'sex'              : 'male' if (Utilities.hex2chr(response[112:114]) == '\x01') else 'female',
                'age'              : Utilities.hex2dec(response[114:116]),
                'weight_pounds'    : Utilities.hex2dec(response[116:120]),
                'weight_kilos'     : Utilities.hex2dec(response[120:124]),
                'height_inches'      : Utilities.hex2dec(response[124:128]),
                'height_centimeters' : Utilities.hex2dec(response[128:132]),
                'waypoint_count'   : Utilities.hex2dec(response[132:134]),
                'trackpoint_count' : Utilities.hex2dec(response[133:138]),
                'birth_year'       : Utilities.hex2dec(response[138:142]),
                'birth_month'      : Utilities.hex2dec(response[142:144])+1,
                'birth_day'        : Utilities.hex2dec(response[144:146])
            }
            return unit
        else:
            raise GH600ParseException('Unit Information', len(hex), 180)
            



    
