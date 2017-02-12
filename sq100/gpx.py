from lxml import etree


def tracks_to_gpx(tracks, filename):
    gpx_ns = "http://www.topografix.com/GPX/1/1"
    gpx_ns_def = "http://www.topografix.com/GPX/1/1/gpx.xsd"
    xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"
    gar_ns = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2'
    gar_ns_def = "https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd"

    gpx = etree.Element('gpx', nsmap={None: gpx_ns, 'xsi': xsi_ns,
                                      'garmin': gar_ns})

    gpx.set('version', '1.1')
    gpx.set("creator", 'https://github.com/tnachstedt/sq100')
    gpx.set(etree.QName(xsi_ns, "schemaLocation"),
            "%s %s %s %s" % (gpx_ns, gpx_ns_def, gar_ns, gar_ns_def))

    track = etree.Element(etree.QName(gpx_ns, "track"))
    lap = etree.Element(etree.QName(gpx_ns, "trkseg"))

    track.append(lap)
    gpx.append(track)

    doc = etree.ElementTree(gpx)
    doc.write("test.xml",
              encoding="UTF-8",
              xml_declaration=True,
              method='xml',
              pretty_print=True)


if __name__ == '__main__':
    tracks_to_gpx([], '')
