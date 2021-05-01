"""
    Southampton University Formula Student Team Back-End
    Copyright (C) 2021 Nathan Rowley-Smith

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


class _Privilege:
    def __str__(self):
        raise NotImplementedError

    def __int__(self):
        raise NotImplementedError


class _PrivilegeAnon(_Privilege):
    def __str__(self):
        return 'Anon'

    def __int__(self):
        return 0


class _PrivilegeBasic(_Privilege):
    def __str__(self):
        return 'Basic'

    def __int__(self):
        return 1


class _PrivilegeAdmin(_Privilege):
    def __str__(self):
        return 'Admin'

    def __int__(self):
        return 2


class _PrivilegeDeveloper(_Privilege):
    def __str__(self):
        return 'Developer'

    def __int__(self):
        return 3


anon = _PrivilegeAnon()
basic = _PrivilegeBasic()
admin = _PrivilegeAdmin()
developer = _PrivilegeDeveloper()

_strings = {str(anon): anon, str(basic): basic, str(admin): admin, str(developer): developer}


def from_string(string):
    if string in _strings:
        return _strings[string]
    else:
        raise Exception('Invalid privilege string')
