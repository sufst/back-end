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
import flask_restful
import json
import flask
from users import usersManager
import flask_jwt_extended

__all__ = ["Login", "User"]


class Login(flask_restful.Resource):
    @staticmethod
    def post():
        request = json.loads(flask.request.data)
        try:
            token = usersManager.auth_user(request["username"], request["password"])
        except KeyError:
            return {"msg": "Bad username or password"}, 401
        else:
            return flask.jsonify(access_token=token)


class User(flask_restful.Resource):
    @staticmethod
    @flask_jwt_extended.jwt_required()
    def get():
        return flask_jwt_extended.current_user.meta

    @staticmethod
    def post():
        data = json.loads(flask.request.data)

        if "username" not in data or "password" not in data or "meta" not in data:
            return data, 400

        try:
            usersManager.create_user(data["username"], data["password"], data["meta"])
        except KeyError:
            return data, 409
