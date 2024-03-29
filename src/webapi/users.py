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
from src.helpers import privileges, departments
import json


def _on_users_post() -> str or tuple:
    data = webapi.request.get_json()

    fields = [
        'password',
        'privilege',
        'department',
        'meta'
    ]

    if not set(data.keys()) == set(fields):
        return 'Missing user args', 400

    user = webapi.request.wanted_user
    password = data['password']
    privilege = data['privilege']
    department = data['department']
    meta = data['meta']

    try:
        user.create(password, privilege, department, meta)
        return '', 200
    except Exception as error:
        print(error)
        return str(error), 409


def _on_users_get() -> str or tuple:
    u = webapi.request.wanted_user

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


def _on_users_patch_username(new: str) -> None:
    u = webapi.request.wanted_user
    u.update_username(new)


def _on_users_patch_password(new: str) -> None:
    u = webapi.request.wanted_user
    u.update_password(new)


def _on_users_patch_meta(new: str) -> None:
    k, v = new
    u = webapi.request.wanted_user
    u.update_meta(k, v)


def _on_users_patch_privilege(new: str) -> None:
    u = webapi.request.wanted_user
    u.update_privilege(new)


def _on_users_patch_department(new: str) -> None:
    u = webapi.request.wanted_user
    u.update_department(new)


def _on_users_patch() -> str or tuple:
    data = webapi.request.get_json()

    handlers = {
        'username': lambda new: _on_users_patch_username(new),
        'password': lambda new: _on_users_patch_password(new),
        'meta': lambda new: _on_users_patch_meta(new),
        'privilege': lambda new: _on_users_patch_privilege(new),
        'department': lambda new: _on_users_patch_department(new)
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


def _on_all_users_get() -> str or tuple:
    data = users.fetch_all_users()

    response = {
        "users": []
    }

    if data is not None:
        for user in data:
            privilege = str(privileges.from_level(user[3]))
            department = str(departments.from_number(user[4]))

            user_object = {
                "id": user[0],
                "username": user[1],
                "creation": user[2],
                "privilege": privilege,
                "department": department
            }
            response["users"].append(user_object)

        return response, 200
    else:
        return 'Something went wrong', 501


@webapi.endpoint('/users/<user>', methods=['POST', 'GET', 'PATCH'])
@privileges.privilege_required(privileges.admin)
def _users(user: str) -> str or tuple:
    users.prepare_request(user)

    return webapi.route({
        'POST': lambda: _on_users_post(),
        'GET': lambda: _on_users_get(),
        'PATCH': lambda: _on_users_patch()
    })


@webapi.endpoint('/users', methods=['GET'])
@privileges.privilege_required(privileges.admin)
def _all_users() -> str or tuple:
    return webapi.route({
        'GET': lambda: _on_all_users_get(),
    })

