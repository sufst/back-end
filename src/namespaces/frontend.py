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
import flask
import common.utils


class FrontEnd(flask_socketio.Namespace):
    def __init__(self, namespace):
        super().__init__(namespace)

        self._clients = {}

    @common.utils.authenticated_only
    def on_connect(self):
        if flask_login.current_user.is_authenticated:
            print(f"{flask_login.current_user.username} connected to {self.namespace}")
        else:
            raise ConnectionRefusedError("Unauthorized user")

    @common.utils.authenticated_only
    def on_message(self, data):
        print(f"message received {data} from {flask_login.current_user.username}")

    @common.utils.authenticated_only
    def on_config(self, data):
        config = json.loads(data)
        print(f"config received with {config} from {flask_login.current_user.username}")
        if config["emulation"]:
            sid = flask.request.sid

            @common.utils.set_interval(config["interval"])
            def interval_emit():
                print(f"emit {json.dumps({'rpm': 2})} to {sid}")
                self.emit("data", data=json.dumps({"rpm": 2}), room=sid)

            self._clients[flask_login.current_user.username] = interval_emit()

    def on_disconnect(self):
        if not flask_login.current_user.is_anonymous:
            print(f"{flask_login.current_user.username} disconnected")
            if flask_login.current_user.username in self._clients:
                self._clients[flask_login.current_user.username].set()
