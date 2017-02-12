from sq100.utilities import Utilities

import configparser
import os


class ExportFormat(object):

    def __init__(self, format):
        if os.path.exists(Utilities.getAppPrefix('exportTemplates',
                                                 '%s.txt' % format)):

            templateConfig = configparser.SafeConfigParser({
                'nicename': "%(default)s",
                'extension': "%(default)s",
                'hasMultiple': "false",
            })
            templateConfig.read(
                Utilities.getAppPrefix('exportTemplates', 'formats.ini'))
            if not templateConfig.has_section(format):
                templateConfig.add_section(format)

            self.name = format
            self.nicename = templateConfig.get(
                format, 'nicename', vars={'default': format})
            self.extension = templateConfig.get(
                format, 'extension', vars={'default': format})
            self.hasMultiple = templateConfig.getboolean(format, 'hasMultiple')
        else:
            self.logger.error('%s: no such export format' % format)
            raise ValueError('%s: no such export format' % format)

    def __str__(self):
        return "%s" % self.name

    def exportTrack(self, track, path, **kwargs):
        self.__export([track], path, **kwargs)

    def exportTracks(self, tracks, path, **kwargs):
        if 'merge' in kwargs and kwargs['merge']:
            self.__export(tracks, path, **kwargs)
        else:
            for track in tracks:
                self.exportTrack(track, path, **kwargs)

    def __export(self, tracks, path, **kwargs):
        if os.path.exists(Utilities.getAppPrefix('exportTemplates', 'pre',
                                                 '%s.py' % self.name)):
            sys.path.append(Utilities.getAppPrefix('exportTemplates', 'pre'))
            pre_processor = __import__(self.name)
            for track in tracks:
                pre_processor.pre(track)

        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(
            path, "%s.%s" % (tracks[0].date.strftime("%Y-%m-%d_%H-%M-%S"),
                             self.extension))
        # first arg is for compatibility reasons
        t = Template.from_file(
            Utilities.getAppPrefix('exportTemplates', '%s.txt' % self.name))
        rendered = t.render(tracks=tracks, track=tracks[0])

        with open(path, 'wt') as f:
            f.write(rendered)
