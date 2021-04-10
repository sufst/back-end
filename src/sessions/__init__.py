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
from database import database, Document
import functools
from time import time

__all__ = ["sessions", "Session"]


class Session:
    def __init__(self, name, sensors=None):
        self.name = name
        self.sensors = sensors
        self.running = False

    def get(self):
        if not self.running:
            try:
                documents = database.find_session_collection(self.name)

                # Now the fun of mapping the sessions data entries to sensor data... :)
                wanted_sensors = []
                list(map(
                    lambda x: wanted_sensors.append(x.sensor) if hasattr(x, "sensor") and
                                                                 x.sensor not in wanted_sensors else False,
                    documents))

                data = {}
                for sensor in wanted_sensors:
                    wanted_data = database.find_from_sensor_many_from_ids(
                        sensor,
                        list(map(lambda x: x.mapping,
                                 list(filter(lambda x: hasattr(x, "sensor") and x.sensor == sensor, documents))
                                 ))
                    )
                    data[sensor] = {
                        "meta": database.find_from_sensor_many(sensor, {"id": [wanted_data[0].meta_id]})[0].__dict__,
                        "data": list(map(lambda x: {"value": x.value, "epoch": x.epoch}, wanted_data))
                    }

                return data
            except KeyError as error:
                raise error
        else:
            raise KeyError(f"Cannot get session {self.name} as active")

    def start(self):
        self.running = True

    def end(self):
        self.running = False

    def insert_sensor_data_mappings(self, mappings):
        if self.running:
            creation = time()
            wanted_ids = list(filter(lambda entry: entry[0] in self.sensors, mappings.items()))

            insertions = []
            for sensor, ids in wanted_ids:
                insertions.extend(list(map(lambda x: Document(
                    {"sensor": sensor, "creation": creation, "mapping": x}), ids)))

            database.insert_to_session_many(self.name, insertions)


class SessionsManager:
    sessions = {}

    def create(self, session):
        """
        Create a new session and places it in the inactive session table.
        Raises a KeyError if the session already exists.

        :param session: The session instance to create.
        """
        if session.name not in self.sessions:
            entry = {"creation": time(), "sensors": session.sensors}
            try:
                database.insert_session_collection(session.name, Document(entry))
            except KeyError as error:
                raise error
            else:
                self.sessions[session.name] = session
        else:
            raise KeyError(f"Session {session.name} already exists")

    def list(self):
        """
        Get all active and stored sessions names.
        """
        return {
            "active": list(self.sessions.keys()),
            "stored": database.list_all_session_collections()
        }

    def get(self, name):
        """
        Get a session instance.
        Raises KeyError if the session does not exist.

        :param name: Name of the session.
        """      
        if name in self.sessions:
            return self.sessions[name]
        else:
            if name in database.list_all_session_collections():
                return Session(name)
            else:
                raise KeyError(f"Session {name} does not exist")

    def sensors_data_insertion_hook(self):
        """
        A decorator hook which is for the sensor insert_sensors_data function.

        The hook allows us to obtain the IDs of the inserted IDs (which is returned by insert_sensors_data)
        in a non-invasive way. The insert_sensors_data does not need to know what we do with the IDs.
        """
        def wrapper(func):
            @functools.wraps(func)
            def decorator(*args, **kwargs):
                sensors_ids = func(*args, **kwargs)
                for name, session in self.sessions.items():
                    session.insert_sensor_data_mappings(sensors_ids)

                return sensors_ids

            return decorator

        return wrapper


sessions = SessionsManager()
