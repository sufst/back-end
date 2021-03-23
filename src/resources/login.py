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
import common.user
import flask_login
import common.logger


class Login(flask_restful.Resource):
    _userManagement = common.user_management.get_user_management()

    def post(self):
        request = json.loads(flask.request.data)

        user = self._userManagement.get_user_from_username(request["username"])

        if not self._userManagement.is_user_valid(user, request["password"]):
            return {"msg": "Bad username or password"}, 401

        access_token = flask_jwt_extended.create_access_token(identity=user.id)
        self._userManagement.put_access_token_to_user(user, access_token)

        user.authenticated = True
        user.active = True
        if flask_login.login_user(user):
            print(f"logged in {user.username}")

        return flask.jsonify(access_token=access_token)

