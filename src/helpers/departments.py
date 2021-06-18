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
        return 'Electronics'

    def __int__(self) -> int:
        return 0


class _DepartmentAero(_Department): 
    def __str__(self) -> str:
        return 'Aerodynamics'

    def __int__(self) -> int:
        return 1


class _DepartmentOperations(_Department): 
    def __str__(self) -> str:
        return 'Operations'

    def __int__(self) -> int:
        return 2


class _DepartmentPowertrain(_Department): 
    def __str__(self) -> str:
        return 'Powertrain'

    def __int__(self) -> int:
        return 3


class _DepartmentVehiclePerformance(_Department): 
    def __str__(self) -> str:
        return 'Vehicle Performance'

    def __int__(self) -> int:
        return 4


class _DepartmentRaceEngineering(_Department): 
    def __str__(self) -> str:
        return 'Race Engineering'

    def __int__(self) -> int:
        return 5


class _DepartmentTier1(_Department): 
    def __str__(self) -> str:
        return 'Tier 1'

    def __int__(self) -> int:
        return 6


class _DepartmentNone(_Department): 
    def __str__(self) -> str:
        return 'NON SPECIFIED'

    def __int__(self) -> int:
        return 7


elec = _DepartmentElectronics()
aero = _DepartmentAero()
oper = _DepartmentOperations()
powertr = _DepartmentPowertrain()
vehiclePer = _DepartmentVehiclePerformance()
raceEng = _DepartmentRaceEngineering()
tier1 = _DepartmentTier1()
noDept = _DepartmentNone()

_number = {int(elec): elec, int(aero): aero, int(oper): oper, int(powertr): powertr, int(vehiclePer): vehiclePer, int(raceEng): raceEng, int(tier1): tier1, int(noDept): noDept}

_strings = {str(elec): elec, str(aero): aero, str(oper): oper, str(powertr): powertr, str(vehiclePer): vehiclePer, str(raceEng): raceEng, str(tier1): tier1, str(noDept): noDept} 


def from_number(number: int) -> _Department:
    if number in _number:
        return _number[number]
    else:
        raise Exception('Invalid department number')


def from_string(string: str) -> _Department:
    if string in _strings:
        return _strings[string]
    else:
        raise Exception('Invalid department string')