import mock
import struct

from sq100.arival_sq100 import ArivalSQ100


def test_calc_checksum():
    payload=b"\x45\x73\xAF\x20"
    payload_len=struct.pack(">H", len(payload))
    checksum = 0
    checksum^=payload_len[0]
    checksum^=payload_len[1]
    for b in payload:
        checksum^= b
    assert(checksum == ArivalSQ100._calc_checksum(payload))

def test_create_message():
    assert(ArivalSQ100._create_message(0x78) == b'\x02\x00\x01\x78\x79')

def test_unpack_message():
    command = 123
    parameter=b"Hello world"
    payload_length=len(parameter)
    checksum = ArivalSQ100._calc_checksum(parameter)
    message =struct.pack(">BH%dsB" % len(parameter), command, payload_length,
                         parameter, checksum)
    data = ArivalSQ100._unpack_message(message)
    assert(data.command == command)
    assert(data.parameter == parameter)
    assert(data.payload_length == payload_length)
    assert(data.checksum == checksum)