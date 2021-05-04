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
from src.plugins import users, webapi
from src.helpers import privileges
import json


def _on_users_post():
    data = webapi.request.get_json()

    fields = [
        'password',
        'privilege',
        'meta'
    ]

    if not set(data.keys()) == set(fields):
        return 'Missing user args', 400

    user = webapi.request.wanted_user
    password = data['password']
    privilege = data['privilege']
    meta = data['meta']

    try:
        user.create(password, privilege, meta)
        return '', 200
    except Exception as error:
        print(error)
        return str(error), 409


def _on_users_get():
    u = webapi.request.wanted_user

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


def _on_users_patch_username(new):
    u = webapi.request.wanted_user
    u.update_username(new)


def _on_users_patch_password(new):
    u = webapi.request.wanted_user
    u.update_password(new)


def _on_users_patch_meta(new):
    k, v = new
    u = webapi.request.wanted_user
    u.update_meta(k, v)


def _on_users_patch_privilege(new):
    u = webapi.request.wanted_user
    u.update_privilege(new)


def _on_users_patch():
    data = webapi.request.get_json()

    handlers = {
        'username': lambda new: _on_users_patch_username(new),
        'password': lambda new: _on_users_patch_password(new),
        'meta': lambda new: _on_users_patch_meta(new),
        'privilege': lambda new: _on_users_patch_privilege(new)
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


@webapi.endpoint('/users/<user>', methods=['POST', 'GET', 'PATCH'])
@privileges.privilege_required(privileges.admin)
def _users(user):
    users.prepare_request(user)

    return webapi.route({
        'POST': lambda: _on_users_post(),
        'GET': lambda: _on_users_get(),
        'PATCH': lambda: _on_users_patch()
    })
