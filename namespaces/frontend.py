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
import flask_login
import functools


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not flask_login.current_user.is_authenticated:
            flask_socketio.disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


class FrontEnd(flask_socketio.Namespace):
    _userManagement = common.user_management.UserManagement().instance()

    @authenticated_only
    def on_connect(self):
        if flask_login.current_user.is_authenticated:
            print(f"{flask_login.current_user.username} connected to {self.namespace}")
        else:
            raise ConnectionRefusedError("Unauthorized user")

    def on_message(self, data):
        print('message received with ', data)

    def on_event_config(self, data):
        print('config received with ', data)

    def on_disconnect(self):
        print('disconnected from client')
