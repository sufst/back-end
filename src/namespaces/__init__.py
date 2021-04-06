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
from database import database, Document
import flask
from configuration import config

__all__ = ["Emulation", "Car"]


emit_job = None
datastore = {"meta": {}, "sensors": {}}


class Namespace(flask_socketio.Namespace):
    @flask_jwt_extended.jwt_required()
    def on_connect(self):
        global emit_job
        global datastore

        user = flask_jwt_extended.current_user

        print(f"{user.login.username} -> {self.namespace}")

        self.emit("meta", json.dumps(datastore["meta"]), room=flask.request.sid),

    def _data_emitter(self):
        global emit_job
        global datastore

        if datastore["sensors"] != {}:
            try:
                self.emit("data", json.dumps(datastore["sensors"]))
            except Exception as error:
                print(repr(error))
                print("Stopping emit job")
                emit_job.remove()
                emit_job = None

            datastore["sensors"] = {}

    @flask_jwt_extended.jwt_required()
    # We can use jwt_required here as socketio pushes the initial connect request context to the global flask
    # request context (as WebSocket transactions do not have requests, so this spoofs that as if they do)
    def on_meta(self, meta):
        global emit_job
        global datastore

        meta = json.loads(meta)
        user = flask_jwt_extended.current_user

        print(f"{user.login.username} -> {meta}")
        datastore["meta"] = meta
        self.emit("meta", json.dumps(datastore["meta"]))

        if emit_job is not None:
            emit_job.remove()

        print("Starting emit job")
        emit_job = scheduler.add_job(
            self._data_emitter, IntervalTrigger(seconds=config.socket_io["data_emit_interval"]))

    @flask_jwt_extended.jwt_required()
    # We can use jwt_required here as socketio pushes the initial connect request context to the global flask
    # request context (as WebSocket transactions do not have requests, so this spoofs that as if they do)
    def on_data(self, data):
        global emit_job
        global datastore

        data = json.loads(data)
        for sensor, data in data.items():
            if sensor not in datastore["sensors"]:
                datastore["sensors"][sensor] = []
            datastore["sensors"][sensor].extend(data)

    @flask_jwt_extended.jwt_required()
    # We can use jwt_required here as socketio pushes the initial connect request context to the global flask
    # request context (as WebSocket transactions do not have requests, so this spoofs that as if they do)
    def on_disconnect(self):
        user = flask_jwt_extended.current_user

        print(f"{user.login.username} /-> {self.namespace}")


Emulation = Namespace


class Car(Namespace):
    def on_data(self, data):
        global datastore

        data = json.loads(data)
        for sensor, data in data.items():
            if sensor not in datastore["sensors"]:
                datastore["sensors"][sensor] = []
            datastore["sensors"][sensor].append(data)
            # TODO: Save car sensor data to database.
