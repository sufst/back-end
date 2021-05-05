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
import functools
from src.plugins import webapi


class _Privilege:
    def __str__(self) -> str:
        raise NotImplementedError

    def __int__(self) -> int:
        raise NotImplementedError


class _PrivilegeAnon(_Privilege):
    def __str__(self) -> str:
        return 'Anon'

    def __int__(self) -> int:
        return 0


class _PrivilegeBasic(_Privilege):
    def __str__(self) -> str:
        return 'Basic'

    def __int__(self) -> int:
        return 1


class _PrivilegeAdmin(_Privilege):
    def __str__(self) -> str:
        return 'Admin'

    def __int__(self) -> int:
        return 2


class _PrivilegeDeveloper(_Privilege):
    def __str__(self) -> str:
        return 'Developer'

    def __int__(self) -> int:
        return 3


anon = _PrivilegeAnon()
basic = _PrivilegeBasic()
admin = _PrivilegeAdmin()
developer = _PrivilegeDeveloper()

_level = {int(anon): anon, int(basic): basic, int(admin): admin, int(developer): developer}
_strings = {str(anon): anon, str(basic): basic, str(admin): admin, str(developer): developer}


def from_level(level: int) -> _Privilege:
    if level in _level:
        return _level[level]
    else:
        raise Exception('Invalid privilege level')


def from_string(string: str) -> _Privilege:
    if string in _strings:
        return _strings[string]
    else:
        raise Exception('Invalid privilege string')


def privilege_required(privilege: _Privilege) -> callable:
    def decorator(func: callable) -> callable:
        @functools.wraps(func)
        @webapi.jwt_required()
        def wrapper(*args, **kwargs) -> tuple:
            user = webapi.current_user

            if int(user.privilege) >= int(privilege):
                return func(*args, **kwargs)
            else:
                return 'User does not have the privilege', 401

        return wrapper
    return decorator
