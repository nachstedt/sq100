import datetime
from lxml import etree


"namespacces"
gpx_ns = "http://www.topografix.com/GPX/1/1"
gpx_ns_def = "http://www.topografix.com/GPX/1/1/gpx.xsd"
xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"
tpex_ns = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2'
tpex_ns_def = "https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd"


def _bounds_element():
    bounds = etree.Element(etree.QName(gpx_ns, "bounds"))
    bounds.set("minlat", "0")
    bounds.set("minlon", "0")
    bounds.set("maxlat", "0")
    bounds.set("maxlon", "0")
    return bounds


def _datetime_element(namespace, name, value):
    return _string_element(namespace, name, value.isoformat())


def _decimal_element(namespace, name, value):
    return _string_element(namespace, name, "%d" % value)


def _garmin_track_point_extension_element():
    trkptex = etree.Element(etree.QName(tpex_ns, "TrackPointExtension"))
    trkptex.append(_decimal_element(tpex_ns, "hr", 150))
    return trkptex


def _gpx_element():
    nsmap = {None: gpx_ns, 'xsi': xsi_ns, 'garmin': tpex_ns}
    gpx = etree.Element('gpx', nsmap=nsmap)
    gpx.set('version', '1.1')
    gpx.set("creator", 'https://github.com/tnachstedt/sq100')
    gpx.set(etree.QName(xsi_ns, "schemaLocation"),
            "%s %s %s %s" % (gpx_ns, gpx_ns_def, tpex_ns, tpex_ns_def))
    gpx.append(_metadata_element())
    gpx.append(_track_element())
    return gpx


def _metadata_element():
    metadata = etree.Element(etree.QName(gpx_ns, 'metadata'))
    metadata.append(_string_element(gpx_ns, "name", "my name"))
    metadata.append(_string_element(gpx_ns, "desc", "my_description"))
    metadata.append(
        _datetime_element(gpx_ns, "time", datetime.datetime.now()))
    metadata.append(_bounds_element())
    return metadata


def _string_element(namespace, name, value):
    elem = etree.Element(etree.QName(namespace, name))
    elem.text = value
    return elem


def _track_element():
    track = etree.Element(etree.QName(gpx_ns, 'trk'))
    track.append(_string_element(gpx_ns, "name", "GPS track name"))
    track.append(_string_element(gpx_ns, "cmt", "GPS track comment"))
    track.append(_string_element(gpx_ns, "desc", "user description"))
    track.append(_string_element(gpx_ns, "src", "data source"))
    track.append(_string_element(gpx_ns, "number", "1"))
    track.append(_track_segment_element())
    return track


def _track_point_element():
    trkpt = etree.Element(etree.QName(gpx_ns, "trkpt"))
    trkpt.set("lat", "0")
    trkpt.set("lon", "0")
    trkpt.append(_decimal_element(gpx_ns, "ele", 111))
    trkpt.append(_datetime_element(
        gpx_ns, "time", datetime.datetime.now()))
    trkpt.append(_track_point_extensions_element())
    return trkpt


def _track_point_extensions_element():
    extensions = etree.Element(etree.QName(gpx_ns, "extensions"))
    extensions.append(_garmin_track_point_extension_element())
    return extensions


def _track_segment_element():
    segment = etree.Element(etree.QName(gpx_ns, "trkseg"))
    for _ in range(5):
        segment.append(_track_point_element())
    return segment


def tracks_to_gpx(tracks, filename):
    gpx = _gpx_element()
    doc = etree.ElementTree(gpx)
    doc.write("test.xml",
              encoding="UTF-8",
              xml_declaration=True,
              method='xml',
              pretty_print=True)


if __name__ == '__main__':
    tracks_to_gpx([], '')
