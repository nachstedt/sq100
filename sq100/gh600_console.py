#! /usr/bin/env python

import configparser
import glob
import os
import sys
import tabulate

from optparse import OptionParser
from sq100.arival_sq100 import ArivalSQ100
from sq100.export_format import ExportFormat
from sq100.utilities import Utilities

def create_computer():
    config = configparser.SafeConfigParser()
    config.read('config.ini')
    computer = ArivalSQ100(
        port=config['serial'].get("comport", '/dev/ttyUSB0'),
        baudrate=config['serial'].getint("baudrate", 115200),
        timeout=config['serial'].getint("timeout", 2))
    return computer

def tracklist():
    computer = create_computer()
    computer.connect()
    tracks = computer.tracklist()
    computer.disconnect()
    if tracks:
        table = [[track.id, track.date, track.distance, track.duration, 
                  track.calories, track.topspeed, track.trackpointCount, 
                  track.lapCount]
                 for track in tracks]
        headers = ["id", "date", "distance", "duration", "calories", "topspeed",
                   "trkpnts", "laps"]
        print(tabulate.tabulate(table, headers=headers))
    else:
        print('no tracks found')
    pass

def prompt_format():
    print('available export formats:')
    for format in gh.getExportFormats():
        print("[%s] = %s" % (format.name, format.nicename))
    
    format = raw_input("Choose output format: ").strip()
    return format
        

def choose():
    print("""
What do you want to do?\n\
------TRACKS-------\n\
[a]  = get list of all tracks\n\
[b]  = select and export tracks (to default format) | [b?] to select format or [b <format>]\n\
[c]  = export all tracks (to default format)        | [c?] to select format or [c <format>]\n\
[d]  = upload tracks\n\
-----WAYPOINTS-----\n\
[e]  = download waypoints\n\
[f]  = upload waypoints\n\
-----ETC-----------\n\
[gg] = format tracks\n\
[hh] = format waypoints\n\
[i]  = get device information\n\
-------------------\n\
[q] = quit""")

    command = input("=>").strip()
    
    if command == "a":
        print("Getting tracklist")
        tracklist()
    
    elif command.startswith("b"):
        print("Export track(s)")
        
        if command.startswith("b!"):
            command = command[0] + command[2:]
        else:
            tracklist()
        
        picks = input("enter trackID(s) [space delimited] ").strip()
        #adds the slice notation for selecting tracks, i.e. [2:4] or [:-4] or [3]
        if ":" in picks:
            lower, upper = picks.split(':')
            try:
                lower = int(lower)
            except ValueError:
                lower = None
            try:
                upper = int(upper)
            except ValueError:
                upper = None

            trackIds = gh.getAllTrackIds()[lower:upper]
        elif "-" in picks:
            trackIds = [gh.getAllTrackIds()[int(picks)]]
        else:
            trackIds = picks.split(' ')
            
        if command == "b?":
            format = prompt_format()
        elif command.startswith("b "):
            format = command[2:].strip() 
        else:
            format = gh.config.get("export", "default")
            print("FYI: Exporting to default format '%s' (see config.ini)" % format)
        
        ef = ExportFormat(format)
        merge = False
        if ef.hasMultiple and len(trackIds) > 1:
            merge = input("Do you want to merge all tracks into a single file? [y/n]: ").strip()
            merge = True if merge == "y" else False
        
        tracks = gh.getTracks(trackIds)
        gh.exportTracks(tracks, format, merge = merge)
        print('exported %i tracks' % len(tracks))
        
    elif command.startswith("c"):
        print("Export all tracks")
        if command == "c?":
            format = prompt_format()
        elif command.startswith("c "):
            format = command[2:].strip() 
        else:
            format = gh.config.get("export", "default")
            print("FYI: Exporting to default format '%s' (see config.ini)" % format)
        
        tracks = gh.getAllTracks()
        results = gh.exportTracks(tracks, format)
        print('exported %i tracks to %s' % (len(tracks), format))
        
    elif command == "d":
        print("Upload Tracks")
        files = glob.glob(os.path.join(Utilities.getAppPrefix(), "import", "*.gpx"))
        for i,format in enumerate(files):
            (filepath, filename) = os.path.split(format)
            #(shortname, extension) = os.path.splitext(filename)
            print('[%i] = %s' % (i, filename))
        
        fileId = raw_input("enter number(s) [space delimited] ").strip()
        fileIds = fileId.split(' ');
        
        filesToBeImported = []
        for fileId in fileIds:
            filesToBeImported.append(files[int(fileId)])
                    
        tracks = gh.importTracks(filesToBeImported)        
        results = gh.setTracks(tracks)
        print('successfully uploaded tracks ', str(results))
        
    elif command == "e":
        print("Download Waypoints")
        waypoints = gh.getWaypoints()    
        results = gh.exportWaypoints(waypoints)
        print('exported Waypoints to', results)
        
    elif command == "f":
        print("Upload Waypoints")
        waypoints = gh.importWaypoints()        
        results = gh.setWaypoints(waypoints)
        print('Imported %i Waypoints' % results)
        
    elif command == "gg":
        print("Delete all Tracks")
        warning = raw_input("warning, DELETING ALL TRACKS").strip()
        results = gh.formatTracks()
        print('Deleted all Tracks:', results)
        
    elif command == "hh":
        print("Delete all Waypoints")
        warning = raw_input("WARNING DELETING ALL WAYPOINTS").strip()
        results = gh.formatWaypoints()
        print('Formatted all Waypoints:', results)
    
    elif command == "i":
        unit = gh.getUnitInformation()
        print("* %s waypoints on watch" % unit['waypoint_count'])
        print("* %s trackpoints on watch" % unit['trackpoint_count'])
    
    elif command == "x":
        print(prompt_format())
    
    elif command == "q":
        sys.exit()
        
    else:
        print("whatever")
    
    choose()


def main():  
    #use standard console interface
    if not sys.argv[1:]:
        choose()
    #parse command line args
    else:
        usage = 'usage: %prog arg [options]'
        description = 'Command Line Interface for GH-615 Python interface, for list of args see the README'
        parser = OptionParser(usage, description = description)
        #parser.add_option("-a", "--tracklist", help="output a list of all tracks")
        #parser.add_option("-b", "--download-track")
        #parser.add_option("-c", "--download-all-tracks")
        #parser.add_option("-d", "--upload-track")
        #parser.add_option("-e", "--download-waypoints")
        #parser.add_option("-f", "--upload-waypoints")  
        #parser.add_option("-gg","--format-tracks") 
        #parser.add_option("-h", "--connection-test")
        #parser.add_option("-i", "--unit-information") 
        
        parser.set_defaults(
            format = "gpx",
            merge  = False,
            input  = None,
            output = None,
        )
        
        parser.add_option("-t", "--track", help="a track id",  action="append", dest="tracks", type="int")
        parser.add_option("-f", "--format", help="the format to export to (default: %s)" % gh.config.get('export','default'), dest="format", choices=[format.name for format in gh.getExportFormats()])
        parser.add_option("-m", "--merge", help="merge into single file?", dest="merge", action="store_true")
        parser.add_option("-c", "--com", dest="com",  help="the comport to use")
        parser.add_option("-v", "--firmware", dest="firmware", choices=["1","2"], help="firmware version of your GH: (1 for old, 2 for new)")
        
        
        parser.add_option("-i", "--input", help="input file(s)", action="append", dest="input")
        parser.add_option("-o", "--output", help="the path to output to", dest="output")
        
        (options, args) = parser.parse_args()
        
        if len(args) != 1:
            parser.error("incorrect number of arguments")
        
        #set firmware version
        if options.firmware:
            gh.config.set('general', 'firmware', int(options.firmware))
        
        #set serial port
        if options.com:
            gh.config.set('serial', 'comport', options.com)

        if options.output:
            gh.config.set('export', 'path', options.output)
            
        if options.format:
            gh.config.set('export', 'default', options.format)
        
        if args[0] == "a":
            tracklist()
            
        elif args[0] == "b":            
            if not options.tracks:
                parser.error("use option '--track' to select track")
                
            tracks = gh.getTracks(options.tracks)
            gh.exportTracks(tracks, gh.config.get('export', 'default'), gh.config.get('export', 'path'), merge = options.merge)
            
        elif args[0] == "c":        
            tracks = gh.getAllTracks()
            gh.exportTracks(tracks, gh.config.get('export', 'default'), gh.config.get('export', 'path'), merge = options.merge)
            
        elif args[0] == "d":
            if not options.input:
                parser.error("use option '--input' to select files")
            tracks = gh.importTracks(options.input)
            results = gh.setTracks(tracks)
        
        elif args[0] == "e":
            waypoints = gh.getWaypoints()    
            results = gh.exportWaypoints(waypoints, path=options.output)
            
        elif args[0] == "f":
            waypoints = gh.importWaypoints(path=options.input[0])
            results = gh.setWaypoints(waypoints)
            print('Imported Waypoints %i' % results)
            
        elif args[0] == "gg":
            warning = raw_input("warning, DELETING ALL TRACKS").strip()
            results = gh.formatTracks()
            
        elif args[0] == "hh":
            warning = raw_input("warning, DELETING ALL WAYPOINTS").strip()
            results = gh.formatWaypoints()
                    
        elif args[0] == "i":
            return gh.getUnitInformation()
        
        else:
            parser.error("invalid argument, try -h or see README for help")
    
        
if __name__ == "__main__":
    main()