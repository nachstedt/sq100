import datetime
import pytest
from mock import call, create_autospec, MagicMock, patch
from lxml import etree

import sq100.gpx as gpx
from test import test_datetime


def test_bounds_element():
    min_latitude = 10.8
    max_latitude = 25.0
    min_longitude = -8.1
    max_longitude = -2.9
    bounds = gpx._bounds_element(
        min_latitude=min_latitude, max_latitude=max_latitude,
        min_longitude=min_longitude, max_longitude=max_longitude)
    assert float(bounds.get("minlat")) == min_latitude
    assert float(bounds.get("minlon")) == min_longitude
    assert float(bounds.get("maxlat")) == max_latitude
    assert float(bounds.get("maxlon")) == max_longitude


def test_datetime_element_with_tzinfo():
    dt = datetime.datetime(
        year=1987, month=12, day=19, hour=15, minute=30, second=20,
        tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
    elem = gpx._datetime_element(namespace="timo", name="birth", value=dt)
    assert elem.tag == "{timo}birth"
    assert elem.text == "1987-12-19T14:30:20Z"


def test_datetime_element_without_tzinfo():
    dt = datetime.datetime(
        year=1987, month=12, day=19, hour=15, minute=30, second=20)
    elem = gpx._datetime_element(namespace="timo", name="birth", value=dt)
    assert elem.tag == "{timo}birth"
    assert elem.text == "1987-12-19T15:30:20Z"


def test_decimal_element():
    elem = gpx._decimal_element(namespace="timo", name="number", value=-42)
    assert elem.tag == '{timo}number'
    assert int(elem.text) == -42


def test_garmin_track_point_extension_element():
    track_point = MagicMock()
    track_point.heart_rate = 150
    ns = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2'
    elem = gpx._garmin_track_point_extension_element(track_point)
    assert elem.tag == ("{%s}TrackPointExtension" % ns)
    print(etree.tostring(elem))
    assert int(elem.find('{%s}hr' % ns).text) == 150
