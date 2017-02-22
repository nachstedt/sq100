#! /usr/bin/env python

import argparse
import cmd
import configparser
import glob
import os
import sys
import tabulate

from sq100.arival_sq100 import ArivalSQ100


class SQ100(object):

    def __init__(self):
        self.config = configparser.SafeConfigParser()
        self.config.read('config.ini')
        self.computer = None

    def connect(self):
        self.computer = ArivalSQ100(
            port=self.config['serial'].get("comport", '/dev/ttyUSB0'),
            baudrate=self.config['serial'].getint("baudrate", 115200),
            timeout=self.config['serial'].getint("timeout", 2))
        self.computer.connect()

    def delete_all_tracks(self):
        print("Delete all Tracks")
        input("warning, DELETING ALL TRACKS").strip()
        results = self.computer.delete_all_tracks()
        print('Deleted all Tracks:', results)

    def delete_all_waypoints(self):
        print("Delete all Waypoints")
        input("WARNING DELETING ALL WAYPOINTS").strip()
        results = self.computer.delete_all_waypoints()
        print('Formatted all Waypoints:', results)

    def device_info(self):
        unit = self.computer.getUnitInformation()
        print("* %s waypoints on watch" % unit['waypoint_count'])
        print("* %s trackpoints on watch" % unit['trackpoint_count'])

    def download_tracks(self, track_ids=[], format='gpx', merge=False):
        ef = ExportFormat(format)
        tracks = self.computer.get_tracks(track_ids)
        print(tracks)

    def download_waypoints(self):
        print("Download Waypoints")
        waypoints = self.computer.get_waypoints()
        results = self.computer.exportWaypoints(waypoints)
        print('exported Waypoints to', results)

    def export_all_tracks(self):
        pass

    def show_tracklist(self):
        tracks = self.computer.get_track_list()
        if tracks:
            table = [[track.id, track.date, track.distance, track.duration,
                      track.trackpoint_count, track.lap_count,
                      track.memory_block_index]
                     for track in tracks]
            headers = ["id", "date", "distance", "duration",
                       "trkpnts", "laps", "mem. index"]
            print(tabulate.tabulate(table, headers=headers))
        else:
            print('no tracks found')
        pass

    def upload_tracks(self):
        print("Upload Tracks")
        files = glob.glob(
            os.path.join(Utilities.getAppPrefix(), "import", "*.gpx"))
        for i, format in enumerate(files):
            (filepath, filename) = os.path.split(format)
            # (shortname, extension) = os.path.splitext(filename)
            print('[%i] = %s' % (i, filename))

        fileId = input("enter number(s) [space delimited] ").strip()
        fileIds = fileId.split(' ')

        filesToBeImported = []
        for fileId in fileIds:
            filesToBeImported.append(files[int(fileId)])

        tracks = self.computer.import_tracks(filesToBeImported)
        results = self.computer.set_tracks(tracks)
        print('successfully uploaded tracks ', str(results))

    def upload_waypoints(self):
        print("Upload Waypoints")
        waypoints = self.computer.import_waypoints()
        results = self.computer.set_waypoints(waypoints)
        print('Imported %i Waypoints' % results)


class SQ100Shell(cmd.Cmd):
    intro = "Welcome to SQ100. Type help or ? to list commands.\n"
    prompt = '(sq100)'

    def __init__(self):
        self.sq100 = SQ100()

    def do_delete_all_tracks(self):
        "delete all tracks on device"
        self.sq100.delete_all_tracks()

    def do_delete_all_waypoints(self):
        "delete all waypoints on device"
        self.sq100.delete_all_waypoints()

    def do_export(self):
        "export selected tracks into file: export 2,5"
        self.sq100.export_tracks()

    def do_export_all(self):
        "export all tracks"
        self.sq100.export_all_tracks()

    def do_list(self):
        "show list of all tracks on the device: list"
        self.sq100.show_tracklist()

    def do_quit(self, arg):
        "Exit the application"
        return True

    def do_upload(self):
        "upload tracks"
        self.sq100.upload_tracks()
        pass

    def do_wpt_download(self, arg):
        "download waypoints"
        self.sq100.download_waypoints()

    def do_wpt_upload(self, arg):
        "upload waypoints"
        self.sq100.upload_waypoints()


def process_command_line_arguments():
    description = (
        'Serial Communication with the Arival SQ100 heart rate computer')
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        'command',
        help='command to execute',
        choices=['tracklist', 'trackdown'],
        default='tracklist')
    parser.add_argument(
        "-t", "--track",
        help="a track id",
        action="append",
        dest="tracks",
        type="int")
    parser.add_argument(
        "-f", "--format",
        help="the format to export to",
        choices=['gpx'])
    parser.add_option(
        "-m", "--merge",
        help="merge into single file?",
        action="store_true")
    parser.add_option(
        "-c", "--comport",
        help="the comport to use")
    parser.add_option(
        "-i", "--input",
        help="input file(s)",
        action="append")
    parser.add_option(
        "-o", "--output",
        help="the path to output to")

    args = parser.parse_args()

    sq100 = SQ100()

    if args.comport:
        sq100.config.set('serial', 'comport', args.comport)

    if args.command == "tracklist":
        sq100.show_tracklist()

    if args.command == "trackdown":
        if not args.tracks:
            parser.error("use option '--track' to select track")

        sq100.download_tracks(track_ids=args.tracks, merge=args.merge)


def main():
    if not sys.argv[1:]:
        SQ100Shell().cmdloop()
    else:
        process_command_line_arguments()

if __name__ == "__main__":
    main()
