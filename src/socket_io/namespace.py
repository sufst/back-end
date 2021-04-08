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
import flask_jwt_extended
import json
from scheduler import scheduler, IntervalTrigger
import flask
from configuration import config


class Namespace(flask_socketio.Namespace):
    emit_job = None

    # The local datastore is a staging area for data to emit.
    meta = {}
    senses = {}

    @flask_jwt_extended.jwt_required()
    def on_connect(self):
        user = flask_jwt_extended.current_user

        print(f"{user.login.username} -> {self.namespace}")

        if not self.meta == {}:
            self.emit("meta", json.dumps(self.meta), room=flask.request.sid),

    def _data_emitter(self):
        if self.senses != {}:
            try:
                self.emit("data", json.dumps(self.senses))
            except Exception as error:
                print(repr(error))
                print("Stopping emit job")
                self.emit_job.remove()
                self.emit_job = None

            self.senses = {}

    def _schedule_data_emit(self):
        if self.emit_job is not None:
            self.emit_job.remove()

        print("Starting emit job")
        self.emit_job = scheduler.add_job(
            self._data_emitter, IntervalTrigger(seconds=config.socket_io["data_emit_interval"]))

    def _handle_meta(self, meta):
        user = flask_jwt_extended.current_user

        print(f"{user.login.username} -> {meta}")
        self.meta = meta
        self.emit("meta", json.dumps(self.meta))

    def _handle_data(self, data):
        for sensor, data in data.items():
            if sensor not in self.senses:
                self.senses[sensor] = []
            self.senses[sensor].extend(data)

    def on_meta(self, meta):
        pass

    def on_data(self, data):
        pass

    @flask_jwt_extended.jwt_required()
    def on_disconnect(self):
        user = flask_jwt_extended.current_user

        print(f"{user.login.username} /-> {self.namespace}")
