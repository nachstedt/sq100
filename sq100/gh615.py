from gh600 import GH600


class GH615(GH600):
    GH600.COMMANDS.update({
        'setTracks': '02%(payload)s%(isFirst)s%(trackInfo)s%(from)s%(to)s'
                     '%(trackpoints)s%(checksum)s'
    })

    @serial_required
    def getTracklist(self):
        tracklist = self._querySerial('getTracklist')

        if len(tracklist) > 8:
            tracks = Utilities.chop(tracklist[6:-2], 48)  # trim header, wtf?
            self.logger.info('%i tracks found' % len(tracks))
            return [Track().fromHex(track, self.timezone) for track in tracks]
        else:
            self.logger.info('no tracks found')
            pass

    @serial_required
    def getTracks(self, trackIds):
        trackIds = [Utilities.dec2hex(str(id), 4) for id in trackIds]
        payload = Utilities.dec2hex((len(trackIds) * 512) + 896, 4)
        numberOfTracks = Utilities.dec2hex(len(trackIds), 4)
        checksum = Utilities.checkersum(
            "%s%s%s" % (payload, numberOfTracks, ''.join(trackIds)))

        self._writeSerial('getTracks', **{
            'payload': payload, 'numberOfTracks': numberOfTracks,
            'trackIds': ''.join(trackIds), 'checksum': checksum})

        tracks = []
        last = -1
        initializeNewTrack = True

        while True:
            data = self._readSerial(2075)
            time.sleep(2)

            if data != '8A000000':
                # shoud new track be initialized?
                if initializeNewTrack:
                    self.logger.debug('initalizing new track')
                    track = Track().fromHex(data[6:50], self.timezone)
                    initializeNewTrack = False

                if len(data) < 2070:
                    # if (Utilities.hex2dec(data[50:54]) == last + 1):
                    self.logger.debug('getting trackpoints %d-%d' % (
                        Utilities.hex2dec(data[50:54]),
                        Utilities.hex2dec(data[54:58])))
                    track.addTrackpointsFromHex(data[58:-2])
                    # remember last trackpoint
                    last = Utilities.hex2dec(data[54:58])
                    # check if last segment of track
                    if last + 1 == track.trackpointCount:
                        tracks.append(track)
                        last = -1
                        initializeNewTrack = True
                    self._writeSerial('requestNextTrackSegment')
                else:
                    # re-request last segment again
                    self.logger.debug('last segment Errornous, re-requesting')
                    self.serial.flushInput()
                    self._writeSerial('requestErrornousTrackSegment')
            else:
                break

        self.logger.info('number of tracks %d' % len(tracks))
        return tracks

    @serial_required
    def setTracks(self, tracks):
        # TODO: There is currently a problem with uploading tracks with less
        # than 10 trackpoints !?
        for track in tracks:
            chunks = Utilities.chop(hex(track), 4142)
            for i, chunk in enumerate(chunks):
                response = self._querySerial(chunk)

                if response == '9A000000':
                    self.logger.info('successfully uploaded track')
                elif response == '91000000' or response == '90000000':
                    self.logger.debug(
                        "uploaded chunk %i of %i" % (i + 1, len(chunks)))
                elif response == '92000000':
                    # this probably means segment was not as expected, should
                    # resend previous segment?
                    self.logger.debug('wtf')
                else:
                    # print response
                    self.logger.info('error uploading track')
                    raise GH600Exception
        return len(tracks)
