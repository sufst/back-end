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
import flask_login
import json
from users import usersManager
from schedular import scheduler


__all__ = ["Emulation"]


class Emulation(flask_socketio.Namespace):
    @usersManager.authenticated_only
    def on_connect(self):
        print(f"{flask_login.current_user.username} -> /emulation connect")
        # TODO: send sensor configuration

    @usersManager.authenticated_only
    def on_config(self, data):
        config = json.loads(data)
        print(f"{flask_login.current_user.username} -> /emulation {config}")

    @staticmethod
    def on_disconnect():
        if not flask_login.current_user.is_anonymous:
            print(f"{flask_login.current_user.username} -> /emulation disconnect")


# class Car(flask_socketio.Namespace):
#     @users.authenticated_only
#     def on_connect(self):
#         if flask_login.current_user.is_authenticated:
#             print(f"{flask_login.current_user.username} connected to {self.namespace}")
#         else:
#             raise ConnectionRefusedError("Unauthorized user")
#
#     @users.authenticated_only
#     def on_message(self, data):
#         print(f"message received {data} from {flask_login.current_user.username}")
#
#     @users.authenticated_only
#     def on_config(self, data):
#         config = json.loads(data)
#         print(f"config received with {config} from {flask_login.current_user.username}")
#         if config["emulation"]:
#             sid = flask.request.sid
#
#     @staticmethod
#     def on_disconnect():
#         if not flask_login.current_user.is_anonymous:
#             print(f"{flask_login.current_user.username} disconnected")
