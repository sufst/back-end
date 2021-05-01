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
import json


def _on_login_post():
    data = webapi.request.get_json()

    username = data['username']
    password = data['password']

    try:
        token = users.auth_user(username, password)
    except KeyError:
        return {"msg": "Bad username or password"}, 401
    else:
        return json.dumps({'access_token': token})


@webapi.endpoint('/login', methods=['POST'])
def login():
    return webapi.route({
        'POST': lambda: _on_login_post()
    })
