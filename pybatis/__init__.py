# pybatis
# Copyright 2009 Cystems Technology
# Author: Manni Wood (mwood aat cystems-tech.com)

# This file is part of pybatis.
# 
# pybatis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pybatis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with pybatis.  If not, see <http://www.gnu.org/licenses/>.

from jinja2.runtime import Undefined

########### defs

RETURN_EVERYTHING = 0
RETURN_FIRST_ROW = 1
RETURN_FIRST_DATUM = 2

LOG_EVERYTHING = 0  # log all calls to SQLMap object
LOG_PER_CALL = 1  # log based on per-call config of SQLMap object
LOG_NOTHING = 2  # log no calls to SQLMap object

########### custom Jinja tests needed by pybatis

# detect dict val not being present
def is_present(str):
    return (not isinstance(str, Undefined)) and str != None

# detect dict val not being present or being present but empty string
def is_not_empty(str):
    return (not isinstance(str, Undefined)) and str != None and str != ''

########## custom exceptions

class NullConnectionException(Exception):
    pass

class ConnectionClosedException(Exception):
    pass

class CursorAlreadyExistsException(Exception):
    pass

class CursorAlreadyOpenException(Exception):
    pass

class FileAndInlineBothNoneException(Exception):
    pass

