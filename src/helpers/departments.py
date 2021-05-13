"""
    Southampton University Formula Student Team Back-End
    Copyright (C) 2021 SUFST

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

class _Department:
    def __str__(self) -> str:
        raise NotImplementedError

    def __int__(self) -> int:
        raise NotImplementedError

class _DepartmentElectronics(_Department): 
   def __str__(self) -> str:
        return 'Elec'

    def __int__(self) -> int:
        return 0
   
elec = _DepartmentElectronics()

_number = {int(elec): elec}
_strings = {str(elec): elec}

def from_int(number: int) -> _Department:
    if number in _number:
        return _number[number]
    else:
        raise Exception('Invalid department number')


def from_string(string: str) -> _Department:
    if string in _strings:
        return _strings[string]
    else:
        raise Exception('Invalid department string')