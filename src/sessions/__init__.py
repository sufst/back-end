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

__all__ = ["sessions"]


class SessionsManager:
    sessions = {}

    def create_session(self, name, sensors):
        """
        Create a new session and places it in the inactive session table.
        Raises a KeyError if the session already exists.

        :param name: The name of the session.
        :param sensors: The list of sensors to capture.
        """
        entry = {"creation": time(), "sensors": sensors}
        try:
            database.insert_session_collection(name, Document(entry))
        except KeyError as error:
            raise error
        else:
            entry["active"] = False
            self.sessions[name] = entry

    def start_session(self, name):
        """
        Start a session.

        :param name: The name of the session.
        """
        if name in self.sessions and self.sessions[name]["active"] is False:
            self.sessions[name]["active"] = True

    def end_session(self, name):
        """
        End a session.
        Raises KeyError if the session does not exist.

        :param name: The session name.
        """
        if name in self.sessions:
            del self.sessions[name]
        else:
            raise KeyError(f"Session {name} is not active")

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

                creation = time()

                for name in self.sessions:
                    if self.sessions[name]["active"]:
                        wanted_sensors = self.sessions[name]["sensors"]
                        wanted_ids = list(filter(lambda entry: entry[0] in wanted_sensors, sensors_ids.items()))

                        insertions = []
                        for sensor, ids in wanted_ids:
                            insertions.extend(list(map(lambda x: Document(
                                {"sensor": sensor, "creation": creation, "mapping": x}), ids)))

                        database.insert_to_session_many(name, insertions)

                return sensors_ids

            return decorator

        return wrapper


sessions = SessionsManager()
