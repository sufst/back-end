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
import flask_socketio
import flask
import common.user_management


class FrontEnd(flask_socketio.Namespace):
    _userManagement = common.user_management.UserManagement().instance()

    def on_connect(self):
        print("connected")
        access_token = flask.request.args.get("access_token")
        if not self._userManagement.is_valid_access_token(access_token):
            raise ConnectionRefusedError("Unauthorized access token")

        user = self._userManagement.get_user_from_access_token(access_token)

        print(f"{user.username} connected to {self.namespace}")

    def on_message(self, data):
        print('message received with ', data)

    def on_event_config(self, data):
        print('config received with ', data)

    def on_disconnect(self):
        print('disconnected from client')
