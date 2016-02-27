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


class SQ100Exception(Exception):
    pass


class SQ100SerialException(SQ100Exception):
    pass


class SQ100MessageException(SQ100Exception):
    pass
