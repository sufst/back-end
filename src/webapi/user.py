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
from src.helpers import privileges
from src.plugins import webapi
import json


@privileges.privilege_required(privileges.basic)
def _on_user_get() -> str or tuple:
    u = webapi.current_user

    if u is not None:
        d = {
            'username': u.username,
            'creation': u.creation,
            'privilege': str(u.privilege),
            'department': str(u.department),
            'meta': u.meta
        }

        rsp = webapi.Response(json.dumps(d))
        return rsp
    else:
        return None, 404


def _on_user_patch_username(new: str) -> None:
    u = webapi.current_user
    u.update_username(new)


def _on_user_patch_password(new: str) -> None:
    u = webapi.current_user
    u.update_password(new)


def _on_user_patch_meta(new: str) -> None:
    k, v = new
    u = webapi.current_user
    u.update_meta(k, v)


@privileges.privilege_required(privileges.admin)
def _on_user_patch_privilege(new: str) -> None:
    u = webapi.current_user
    u.update_privilege(new)

@privileges.privilege_required(privileges.admin)
def _on_user_patch_department(new: str) -> None:
    u = webapi.current_user
    u.update_department(new)


@privileges.privilege_required(privileges.basic)
def _on_user_patch() -> str or tuple:
    data = webapi.request.get_json()

    handlers = {
        'username': lambda new: _on_user_patch_username(new),
        'password': lambda new: _on_user_patch_password(new),
        'meta': lambda new: _on_user_patch_meta(new),
        'privilege': lambda new: _on_user_patch_privilege(new),
        'department': lambda new: _on_user_patch_department(new)
    }

    args = list(handlers.keys())

    if not list(filter(lambda k: k in args, list(data.keys()))):
        return 'No valid args in request', 400

    try:
        for key, value in data.items():
            if key in handlers:
                handlers[key](value)
        return '', 200
    except Exception as err:
        return repr(err), 400


@webapi.endpoint('/user', methods=['GET', 'PATCH'])
def user() -> str or tuple:
    return webapi.route({
        'GET': lambda: _on_user_get(),
        'PATCH': lambda: _on_user_patch()
    })
