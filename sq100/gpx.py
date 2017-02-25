import datetime
from lxml import etree

from sq100.track import CoordinateBounds
from sq100.point import Point

"namespacces"
gpx_ns = "http://www.topografix.com/GPX/1/1"
gpx_ns_def = "http://www.topografix.com/GPX/1/1/gpx.xsd"
xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"
tpex_ns = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2'
tpex_ns_def = "https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd"


def _calc_tracks_bounds(tracks):
    track_bounds = [t.bounds() for t in tracks]
    min_latitude = min([b.min.latitude for b in track_bounds])
    min_longitude = min([b.min.longitude for b in track_bounds])
    max_latitude = max([b.max.latitude for b in track_bounds])
    max_longitude = max([b.max.longitude for b in track_bounds])
    return CoordinateBounds(
        minimum=Point(latitude=min_latitude, longitude=min_longitude),
        maximum=Point(latitude=max_latitude, longitude=max_longitude))


def _create_bounds_element(value, ns=gpx_ns, tag='bounds',):
    elem = etree.Element(etree.QName(ns, tag))
    elem.set("minlat", str(value.min.latitude))
    elem.set("minlon", str(value.min.longitude))
    elem.set("maxlat", str(value.max.latitude))
    elem.set("maxlon", str(value.max.longitude))
    return elem


def _create_datetime_element(ns, tag, value):
    if value.tzinfo is not None:
        value = (value - value.utcoffset()).replace(tzinfo=None)
    return _create_string_element(ns, tag, "%sZ" % value.isoformat())


def _create_decimal_element(ns, tag, value):
    return _create_string_element(ns, tag, str(value))


def _create_garmin_track_point_extension_element(track_point, ns=tpex_ns,
                                                 tag="garmin"):
    trkptex = etree.Element(etree.QName(ns, tag))
    trkptex.append(
        _create_decimal_element(tpex_ns, "hr", track_point.heart_rate))
    return trkptex


def _create_gpx_element(tracks):
    nsmap = {None: gpx_ns, 'xsi': xsi_ns, 'garmin': tpex_ns}
    gpx = etree.Element('gpx', nsmap=nsmap)
    gpx.set('version', '1.1')
    gpx.set("creator", 'https://github.com/tnachstedt/sq100')
    gpx.set(etree.QName(xsi_ns, "schemaLocation"),
            "%s %s %s %s" % (gpx_ns, gpx_ns_def, tpex_ns, tpex_ns_def))
    gpx.append(_create_metadata_element(bounds=_calc_tracks_bounds(tracks)))
    for i, track in enumerate(tracks):
        gpx.append(_create_track_element(track=track, number=i))
    return gpx


def _create_metadata_element(
        bounds,
        name="SQ100 Tracks",
        description="Tracks export from the SQ100 application",
        date=datetime.datetime.now(),
        ns=gpx_ns, tag='metadata'):
    metadata = etree.Element(etree.QName(ns, tag))
    metadata.append(
        _create_string_element(ns=ns, tag="name", value=name))
    metadata.append(
        _create_string_element(ns=ns, tag="desc", value=description))
    metadata.append(_create_datetime_element(ns=ns, tag="time", value=date))
    metadata.append(_create_bounds_element(ns=ns, tag="bounds", value=bounds))
    return metadata


def _create_string_element(ns, tag, value):
    elem = etree.Element(etree.QName(ns, tag))
    elem.text = value
    return elem


def _create_track_element(track, number, src="Arival SQ100 computer",
                          ns=gpx_ns, tag="trk"):
    elem = etree.Element(etree.QName(ns, tag))
    elem.append(_create_string_element(gpx_ns, "name", track.name))
    elem.append(_create_string_element(gpx_ns, "cmt", "id=%s" % track.id))
    elem.append(_create_string_element(gpx_ns, "desc", track.description))
    elem.append(_create_string_element(gpx_ns, "src", src))
    elem.append(_create_decimal_element(gpx_ns, "number", number))
    elem.append(_create_track_segment_element(track))
    return elem


def _create_track_point_element(track_point, ns=gpx_ns, tag='trkpt'):
    trkpt = etree.Element(etree.QName(ns, tag))
    trkpt.set("lat", str(track_point.latitude))
    trkpt.set("lon", str(track_point.longitude))
    trkpt.append(_create_decimal_element(gpx_ns, "ele", track_point.altitude))
    trkpt.append(_create_datetime_element(gpx_ns, "time", track_point.date))
    trkpt.append(_create_track_point_extensions_element(track_point))
    return trkpt


def _create_track_point_extensions_element(track_point, ns=gpx_ns,
                                           tag="extensions"):
    extensions = etree.Element(etree.QName(ns, tag))
    extensions.append(
        _create_garmin_track_point_extension_element(track_point))
    return extensions


def _create_track_segment_element(track, ns=gpx_ns, tag="trkseg"):
    segment = etree.Element(etree.QName(ns, tag))
    for track_point in track.track_points:
        segment.append(_create_track_point_element(track_point))
    return segment


def tracks_to_gpx(tracks, filename):
    gpx = _create_gpx_element(tracks)
    doc = etree.ElementTree(gpx)
    doc.write(filename,
              encoding="UTF-8",
              xml_declaration=True,
              method='xml',
              pretty_print=True)
