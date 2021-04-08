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
from time import time
from copy import deepcopy
from sessions import sessions

__all__ = ["sensors"]


class SensorsManager:
    latest_meta_ids = {}

    @staticmethod
    def init_sensors(names):
        """
        Initialise new sensors.
        :param names: A list of sensor names.
        """
        for sensor in names:
            database.insert_sensor_collection(
                Document({"name": sensor,
                          "initial": Document({"creation": time(), "type": "initial"})}))

    def insert_sensors_meta(self, metas):
        """
        Insert a dictionary of sensors metas.
        :param metas: The dictionary of metas {<name>: <meta>, ...}
        :return: A corresponding dictionary of inserted IDs.
        """
        ids = {}
        creation = time()

        for sensor, meta in metas.items():
            insert = deepcopy(meta)
            insert.update({"creation": creation, "type": meta})
            ids[sensor] = database.insert_to_sensor_many(sensor, [Document(insert)])[0]

        self.latest_meta_ids = ids
        return ids

    @sessions.sensors_data_insertion_hook()
    def insert_sensors_data(self, datas):
        """
        Insert a dictionary of sensors data.
        :param datas: The dictionary of data {<name>: [<data>,...],...}
        """
        ids = {}
        creation = time()

        for sensor, data in datas.items():
            inserts = list(map(
                lambda x: {"creation": creation,
                           "type": "data",
                           "value": x["value"],
                           "epoch": x["epoch"],
                           "meta_id": self.latest_meta_ids[sensor]},
                data))
            ids[sensor] = database.insert_to_sensor_many(sensor, list(map(lambda x: Document(x), inserts)))

        return ids


sensors = SensorsManager()
