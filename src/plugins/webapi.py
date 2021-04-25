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
from helpers import flask, users
import json


@flask.route('/login', methods=['POST'])
def login():
    if flask.request.method == 'POST':
        data = flask.request.get_json()

        try:
            token = users.auth_user(data['username'], data['password'])
        except KeyError:
            return {"msg": "Bad username or password"}, 401
        else:
            return json.dumps({'access_token': token})
    else:
        return None, 404


@flask.jwt_required()
@flask.route('/user', methods=['GET', 'POST'])
def user():
    if flask.request.method == 'GET':
        return flask.current_user['meta']
    elif flask.request.method == 'POST':
        data = flask.request.get_json()

        meta = {
            "likes_beans": data["likes_beans"] or None
        }

        try:
            print(f"Attempting user create {data['username']} -> {meta}")
            users.create_user(data["username"], data["password"], meta)
        except KeyError as error:
            print(error)
            return str(error), 409
    else:
        return None, 404


def load():
    try:
        users.create_user('intermediate_server', 'sufst', {'likes_beans': True})
    except KeyError:
        pass
    except Exception as err:
        print(err)
