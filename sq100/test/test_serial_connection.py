# SQ100 - Serial Communication with the a-rival SQ100 heart rate computer
# Copyright (C) 2017  Timo Nachstedt
#
# This file is part of SQ100.
#
# SQ100 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SQ100 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mock import patch, MagicMock
import serial
import pytest

from sq100.serial_connection import SerialConnection
from sq100.exceptions import SQ100SerialException


@patch("serial.Serial")
def test_baudrate_getter(MockSerial):
    instance = MockSerial.return_value
    instance.baudrate = 1200
    connection = SerialConnection()
    assert connection.baudrate == 1200


@patch("serial.Serial")
def test_baudrate_setter(MockSerial):
    instance = MockSerial.return_value
    connection = SerialConnection()
    connection.baudrate = 1200
    assert instance.baudrate == 1200


@patch("serial.Serial")
def test_port_getter(MockSerial):
    instance = MockSerial.return_value
    instance.port = "/dev/ttyUSB5"
    connection = SerialConnection()
    assert connection.port == "/dev/ttyUSB5"


@patch("serial.Serial")
def test_port_setter(MockSerial):
    instance = MockSerial.return_value
    connection = SerialConnection()
    connection.port = "/dev/ttyUSB6"
    assert instance.port == "/dev/ttyUSB6"


@patch("serial.Serial")
def test_timeout_getter(MockSerial):
    instance = MockSerial.return_value
    instance.timeout = 5
    connection = SerialConnection()
    assert connection.timeout == 5


@patch("serial.Serial")
def test_timeout_setter(MockSerial):
    instance = MockSerial.return_value
    connection = SerialConnection()
    connection.timeout = 5
    assert instance.timeout == 5


@patch("serial.Serial")
def test_connect_successful(MockSerial):
    instance = MockSerial.return_value
    connection = SerialConnection()
    connection.connect()
    instance.open.assert_called_once_with()


@patch("serial.Serial")
def test_connect_failed(MockSerial):
    instance = MockSerial.return_value
    instance.open.side_effect = serial.SerialException
    connection = SerialConnection()
    with pytest.raises(SQ100SerialException):
        connection.connect()
    instance.open.assert_called_once_with()


@patch("serial.Serial")
def test_disconnect(MockSerial):
    instance = MockSerial.return_value
    connection = SerialConnection()
    connection.disconnect()
    instance.close.assert_called_once_with()


@patch("serial.Serial")
def test_write_successful(MockSerial):
    instance = MockSerial.return_value
    connection = SerialConnection()
    connection.write(b'\x00\x80')
    instance.write.assert_called_once_with(b'\x00\x80')


@patch("serial.Serial")
def test_write_failed(MockSerial):
    instance = MockSerial.return_value
    instance.write.side_effect = serial.SerialTimeoutException
    connection = SerialConnection()
    with pytest.raises(SQ100SerialException):
        connection.write(b'\x00\x80')
    instance.write.assert_called_once_with(b'\x00\x80')


@patch("serial.Serial")
def test_read(MockSerial):
    instance = MockSerial.return_value
    instance.read.return_value = b'\xaa\xbb\xcc'
    connection = SerialConnection()
    assert connection.read(1234) == b'\xaa\xbb\xcc'
    instance.read.assert_called_once_with(1234)


def test_query_succesfull():
    command = b'\xa0\xa1'
    response = b'\xb0\xb1'
    connection = SerialConnection()
    connection.write = MagicMock()
    connection.read = MagicMock(return_value=response)
    assert connection.query(command) == response
    connection.write.assert_called_once_with(command)
    connection.read.assert_called_once_with()


def test_query_succesfull_after_three_tries():
    command = b'\xa0\xa1'
    response = b'\xb0\xb1'
    connection = SerialConnection()
    connection.write = MagicMock()
    connection.read = MagicMock(side_effect=["", "", response])
    assert connection.query(command) == response
    connection.write.assert_called_with(command)
    assert connection.write.call_count == 3
    assert connection.read.call_count == 3


def test_query_fails():
    command = b'\xa0\xa1'
    connection = SerialConnection()
    connection.write = MagicMock()
    connection.read = MagicMock(return_value=b'')
    with pytest.raises(SQ100SerialException):
        connection.query(command)
    assert connection.write.call_count == 3
    assert connection.read.call_count == 3
