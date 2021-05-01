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
from src.plugins import users, webapi
import json


@privileges.privilege_required(privileges.basic)
def _on_user_get():
    u = webapi.current_user

    if u is not None:
        d = {
            'username': u.username,
            'creation': u.creation,
            'privilege': str(u.privilege),
            'meta': u.meta
        }

        rsp = webapi.Response(json.dumps(d))
        return rsp
    else:
        return None, 404


@privileges.privilege_required(privileges.admin)
def _on_user_post():
    data = webapi.request.get_json()

    username = data['username']
    password = data['password']
    privilege = data['privilege']
    meta = data['meta']

    try:
        users.create_user(username, password, privilege, meta)
        return '', 200
    except Exception as error:
        print(error)
        return str(error), 409


@privileges.privilege_required(privileges.basic)
def _on_user_patch():
    return None, 409


@webapi.endpoint('/user', methods=['GET', 'POST', 'PATCH'])
def user():
    return webapi.route({
        'GET': lambda: _on_user_get(),
        'POST': lambda: _on_user_post(),
        'PATCH': lambda: _on_user_patch()
    })
