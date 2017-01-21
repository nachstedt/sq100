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
