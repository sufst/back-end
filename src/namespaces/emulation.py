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
import common.configuration
import common.logger
import time


class EmulationModules:
    def __init__(self, modules):
        for key in modules:
            setattr(self, key, modules[key])


class Emulation(flask_socketio.Namespace):
    def __init__(self, namespace):
        super().__init__(namespace)

        self._clients = {}
        self._emulation_data = []
        self._emulation_data_entry_id = 0
        self._emulation_counter = 0
        self._emulation_modules = None
        self._config = common.configuration.get_configuration_manager().configuration["emulation"]
        self._sensors_config = common.configuration.get_configuration_manager().configuration["sensors"]
        self._logger = common.logger.get_logger(__name__, self._config["verbose"])
        self._emulations = {}
        self._x = 0

        self._build_sensor_emulations()

        @common.utils.set_interval(self._config["delay"])
        def spawner():
            if len(self._emulation_data) >= int(5/self._config["delay"]):
                self._emulation_data.pop(0)

            self._emulation_data.append({"id": self._emulation_data_entry_id, "data": self._get_next_emulation()})
            self._emulation_data_entry_id += 1

        self._emulation_spawner = spawner()

    def _build_sensor_emulations(self):
        for sensor, meta in self._sensors_config.items():
            if meta["enable"]:
                self._emulations[sensor] = meta["emulation"]

        modules = {}

        for name, module in self._config["modules"].items():
            modules[name] = __import__(module)

        self._emulation_modules = EmulationModules(modules)

    def _get_next_emulation(self):
        data = {}

        for sensor, emulation in self._emulations.items():
            data[sensor] = {
                "value": (lambda x, modules: eval(emulation))(self._x, self._emulation_modules),
                "epoch": round(time.time(), 3)
            }

        self._x += 1

        return data

    @common.utils.authenticated_only
    def on_connect(self):
        if flask_login.current_user.is_authenticated:
            self._logger.info(f"{flask_login.current_user.username} connected to {self.namespace}")

            sid = flask.request.sid

            connect_config = {
                "spawn_interval": self._config["delay"],
                "sensors_config": self._sensors_config
            }

            self.emit("data", data=json.dumps(connect_config), room=sid)
        else:
            raise ConnectionRefusedError("Unauthorized user")

    @common.utils.authenticated_only
    def on_message(self, data):
        self._logger.debug(f"message received {data} from {flask_login.current_user.username}")

    @common.utils.authenticated_only
    def on_config(self, data):
        username = flask_login.current_user.username
        config = json.loads(data)

        self._logger.info(f"config received with {config} from {username}")
        sid = flask.request.sid

        if username in self._clients:
            self._clients[username].set()

        @common.utils.set_interval(config["interval"])
        def interval_emit(last_emit_id):
            emulation_data = []

            for entry in self._emulation_data:
                if entry["id"] > last_emit_id:
                    emulation_data.insert(0, entry["data"])

            if len(emulation_data) > 0:
                self.emit("data", data=json.dumps(emulation_data), room=sid)
                self._logger.debug(f"{username} <- \n{common.logger.prettify(emulation_data)}")

                self._clients[username].set()
                self._clients[username] = interval_emit(self._emulation_data[-1]["id"])

        self._clients[username] = interval_emit(self._emulation_data[-1]["id"])

    def on_disconnect(self):
        if not flask_login.current_user.is_anonymous:
            self._logger.info(f"{flask_login.current_user.username} disconnected")
            if flask_login.current_user.username in self._clients:
                self._clients[flask_login.current_user.username].set()
