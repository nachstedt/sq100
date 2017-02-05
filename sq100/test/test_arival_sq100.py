import datetime
import mock
import struct

from sq100.arival_sq100 import ArivalSQ100


def test_calc_checksum():
    payload = b"\x45\x73\xAF\x20"
    payload_len = struct.pack(">H", len(payload))
    checksum = 0
    checksum ^= payload_len[0]
    checksum ^= payload_len[1]
    for b in payload:
        checksum ^= b
    assert(checksum == ArivalSQ100._calc_checksum(payload))


def test_create_message():
    assert(ArivalSQ100._create_message(0x78) == b'\x02\x00\x01\x78\x79')


def test_unpack_message():
    command = 123
    parameter = b"Hello world"
    payload_length = len(parameter)
    checksum = ArivalSQ100._calc_checksum(parameter)
    message = struct.pack(">BH%dsB" % len(parameter), command, payload_length,
                          parameter, checksum)
    data = ArivalSQ100._unpack_message(message)
    assert(data.command == command)
    assert(data.parameter == parameter)
    assert(data.payload_length == payload_length)
    assert(data.checksum == checksum)


def test_unpack_track_info_parameter():
    date = datetime.datetime(2016, 7, 23, 14, 30, 11)
    no_track_points = 1230
    duration = datetime.timedelta(seconds=2345)
    distance = 4321
    no_laps = 3
    memory_block_index = 51
    track_id = 13
    calories = 714
    max_speed = 89
    max_heart_rate = 198
    avg_heart_rate = 153
    asc_height = 873
    des_height = 543
    min_height = 345
    max_height = 1122

    parameter = struct.pack(
        ">6B3I5HB3H2B4H13s",
        date.year - 2000, date.month, date.day,
        date.hour, date.minute, date.second,
        no_track_points, duration.seconds * 10, distance,
        no_laps, 0, memory_block_index, 0, track_id,
        0,
        calories, 0, max_speed,
        max_heart_rate, avg_heart_rate,
        asc_height, des_height, min_height, max_height,
        b'')

    track = ArivalSQ100._unpack_track_info_parameter(parameter)
    assert(track.date == date)
    assert(track.no_track_points == no_track_points)
    assert(track.duration == duration)
    assert(track.distance == distance)
    assert(track.no_laps == no_laps)
    assert(track.memory_block_index == memory_block_index)
    assert(track.id == track_id)
    assert(track.calories == calories)
    assert(track.max_speed == max_speed)
    assert(track.max_heart_rate == max_heart_rate)
    assert(track.avg_heart_rate == avg_heart_rate)
    assert(track.ascending_height == asc_height)
    assert(track.descending_height == des_height)
    assert(track.min_height == min_height)
    assert(track.max_height == max_height)
