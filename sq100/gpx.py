import datetime
from lxml import etree


"namespacces"
gpx_ns = "http://www.topografix.com/GPX/1/1"
gpx_ns_def = "http://www.topografix.com/GPX/1/1/gpx.xsd"
xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"
tpex_ns = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2'
tpex_ns_def = "https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd"


def _bounds_element(min_latitude, max_latitude, min_longitude, max_longitude):
    bounds = etree.Element(etree.QName(gpx_ns, "bounds"))
    bounds.set("minlat", str(min_latitude))
    bounds.set("minlon", str(min_longitude))
    bounds.set("maxlat", str(max_latitude))
    bounds.set("maxlon", str(max_longitude))
    return bounds


def _datetime_element(namespace, name, value):
    if value.tzinfo is not None:
        value = (value - value.utcoffset()).replace(tzinfo=None)
    return _string_element(namespace, name, "%sZ" % value.isoformat())


def _decimal_element(namespace, name, value):
    return _string_element(namespace, name, "%d" % value)


def _garmin_track_point_extension_element(track_point):
    trkptex = etree.Element(etree.QName(tpex_ns, "TrackPointExtension"))
    trkptex.append(_decimal_element(tpex_ns, "hr", track_point.heart_rate))
    return trkptex


def _gpx_element(tracks):
    nsmap = {None: gpx_ns, 'xsi': xsi_ns, 'garmin': tpex_ns}
    gpx = etree.Element('gpx', nsmap=nsmap)
    gpx.set('version', '1.1')
    gpx.set("creator", 'https://github.com/tnachstedt/sq100')
    gpx.set(etree.QName(xsi_ns, "schemaLocation"),
            "%s %s %s %s" % (gpx_ns, gpx_ns_def, tpex_ns, tpex_ns_def))
    gpx.append(_metadata_element())
    for i, track in enumerate(tracks):
        gpx.append(_track_element(track, i))
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


def _track_element(track, number):
    trk = etree.Element(etree.QName(gpx_ns, 'trk'))
    trk.append(_string_element(gpx_ns, "name", "GPS track name"))
    trk.append(_string_element(gpx_ns, "cmt", track.id))
    trk.append(_string_element(gpx_ns, "desc", "user description"))
    trk.append(_string_element(gpx_ns, "src", "Arival SQ100 computer"))
    trk.append(_string_element(gpx_ns, "number", number))
    trk.append(_track_segment_element(track))
    return trk


def _track_point_element(track_point):
    trkpt = etree.Element(etree.QName(gpx_ns, "trkpt"))
    trkpt.set("lat", track_point.latitude)
    trkpt.set("lon", track_point.longitude)
    trkpt.append(_decimal_element(gpx_ns, "ele", track_point.altitude))
    trkpt.append(_datetime_element(gpx_ns, "time", track_point.time))
    trkpt.append(_track_point_extensions_element(track_point))
    return trkpt


def _track_point_extensions_element(track_point):
    extensions = etree.Element(etree.QName(gpx_ns, "extensions"))
    extensions.append(_garmin_track_point_extension_element(track_point))
    return extensions


def _track_segment_element(track):
    segment = etree.Element(etree.QName(gpx_ns, "trkseg"))
    for track_point in track.track_points:
        segment.append(_track_point_element(track_point))
    return segment


def tracks_to_gpx(tracks, filename):
    gpx = _gpx_element(tracks)
    doc = etree.ElementTree(gpx)
    doc.write(filename,
              encoding="UTF-8",
              xml_declaration=True,
              method='xml',
              pretty_print=True)
