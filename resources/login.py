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
import flask_jwt_extended
import flask_restful
import flask
import common.user_management
import json


class Login(flask_restful.Resource):
    _user_management = common.user_management.UserManagement().instance()

    def post(self):
        request = json.loads(flask.request.data)

        if not self._user_management.is_user_password_correct(request["username"], request["password"]):
            return {"msg": "Bad username or password"}, 401

        access_token = flask_jwt_extended.create_access_token(identity=request["username"])
        return flask.jsonify(access_token=access_token)

