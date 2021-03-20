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
import common.user_management
import common.user
import flask_jwt_extended


class Users(flask_restful.Resource):
    _user_management = common.user_management.UserManagement().instance()

    """
    users
    """

    @flask_jwt_extended.jwt_required()
    def get(self, username):
        """
        get
        """
        user = self._user_management.get_user_from_user_id(flask_jwt_extended.get_jwt_identity())

        return {"username": user.username, "beans": True}

    def post(self, username):
        """
        post
        """
        meta = json.loads(flask.request.data)

        if self._user_management.create_user(username, meta):
            return meta
        else:
            return meta, 409



