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

import csv
import os
from src.plugins import db, webapi
from time import time
import json
from src.helpers import config, zip
import functools


class Sessions(db.Table):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'name TEXT NOT NULL',
        'creation REAL NOT NULL',
        'status TEXT NOT NULL',
        'sensors TEXT NOT NULL'
    ]


class SessionNotFoundError(Exception):
    pass


class Session:
    _location = ''

    def __init__(self, name: str = None, from_sql: bool = False):
        self._name = name

        if from_sql:
            self._tab = Sessions()

            sql = f'SELECT status, sensors FROM {self._tab.name} WHERE name = ?'
            results = self._tab.execute(sql, (name,))

            if results:
                self._status, j_sensors = results[0]
                self._sensors = json.loads(j_sensors)
            else:
                self._status = None
                self._sensors = None
        else:
            self._status = None
            self._sensors = None
            self._tab = Sessions()

        self._meta = None
        self._data = None
        self._notes = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def sensors(self) -> dict:
        if self._sensors is None:
            sql = f'SELECT sensors FROM {self._tab.name} WHERE name = ?'
            result = self._tab.execute(sql, (self._name,))

            for sensors, in result:
                self._sensors = json.loads(sensors)

        return self._sensors

    @property
    def meta(self) -> str:
        if self._meta is None:
            with open(f'{self._location}/{self._name}/meta.json', 'r') as f:
                self._meta = json.load(f)

        return self._meta

    @property
    def is_exists(self) -> bool:
        if self._name is not None:
            sql = f'SELECT name FROM {self._tab.name} WHERE name = ?'
            results = self._tab.execute(sql, (self._name,))

            if results:
                if not os.path.exists(f'{self._location}/{self._name}'):
                    sql = f'DELETE FROM {self._tab.name} WHERE name = ?'
                    self._tab.execute(sql, (self._name,))

                    return False
                return True
            else:
                return False
        else:
            return False

    @property
    def status(self) -> str:
        if self._status is None:
            sql = f'SELECT status FROM {self._tab.name} WHERE name = ?'
            result = self._tab.execute(sql, (self._name,))

            for status, in result:
                self._status = status

        return self._status

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = {}

            for sensor in self.sensors:
                self._data[sensor] = []
                with open(f'{self._location}/{self._name}/data/{sensor}.csv', 'r', newline='') as f:
                    fieldnames = ['epoch', 'value']
                    reader = csv.DictReader(f, fieldnames=fieldnames)
                    rows = iter(reader)

                    next(rows)
                    for row in rows:
                        self._data[sensor].append({'epoch': row['epoch'], 'value': row['value']})

        return self._data

    @property
    def notes(self) -> list:
        if self._notes is None:
            self._notes = []

            with open(f'{self._location}/{self._name}/notes.csv', 'r', newline='') as f:
                fieldnames = ['epoch', 'note']
                reader = csv.DictReader(f, fieldnames=fieldnames)
                rows = iter(reader)

                next(rows)
                for row in rows:
                    self._notes.append({'epoch': row['epoch'], 'note': row['note']})

        return self._notes

    def create(self, sensors: list, meta: dict) -> None:
        if not self.is_exists:
            self._sensors = sensors
            self._meta = meta

            now = time()

            self._meta.update({'creation': now, 'sensors': self._sensors})

            if not os.path.exists(f'{self._location}/{self._name}/'):
                os.mkdir(f'{self._location}/{self._name}/')

            self._status = 'alive'

            sql = f'INSERT INTO {self._tab.name} (name, creation, status, sensors) VALUES (?,?,?,?)'
            self._tab.execute(sql, (self._name, now, self._status, json.dumps(self._sensors)))

            with open(f'{self._location}/{self._name}/meta.json', 'w') as f:
                json.dump(self._meta, f, indent=4, sort_keys=True)

            with open(f'{self._location}/{self._name}/notes.csv', 'w', newline='') as f:
                fieldnames = ['id, epoch', 'note']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

            os.mkdir(f'{self._location}/{self._name}/data')

            for sensor in self._sensors:
                with open(f'{self._location}/{self._name}/data/{sensor}.csv', 'w', newline='') as f:
                    fieldnames = ['id, epoch', 'value']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
        else:
            raise KeyError('Session already exists')

    @classmethod
    def set_location(cls, location: str) -> None:
        cls._location = location

    def add_sensor_data(self, sensor: str, data: list) -> None:
        rows = list(map(lambda entry: {'epoch': entry['epoch'], 'value': entry['value']}, data))

        with open(f'{self._location}/{self._name}/data/{sensor}.csv', 'a', newline='') as f:
            fieldnames = ['epoch', 'value']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(rows)

    def _zip_session(self) -> None:
        if os.path.exists(f'{self._location}/{self._name}'):
            try:
                zip.zip_folder(f'{self._location}/{self._name}', f'{self._location}/{self._name}/{self._name}.zip')
            except FileExistsError:
                print(f'{self._name}.zip already exists')

    @property
    def zip_path(self) -> str:
        if not os.path.exists(f'{self._location}/{self._name}/{self._name}.zip'):
            self._zip_session()

        return f'{self._location}/{self._name}/{self._name}.zip'

    def add_note(self, note: str) -> None:
        with open(f'{self._location}/{self._name}/notes.csv', 'a', newline='') as f:
            fieldnames = ['epoch', 'note']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow({'epoch': time(), 'note': note})

    def stop(self) -> None:
        self._status = 'dead'
        sql = f'UPDATE {self._tab.name} SET status = ? WHERE name = ?'
        self._tab.execute(sql, (self._status, self._name, ))


class SessionsManager:
    _location = ''

    def __init__(self):
        self._tab = Sessions()

    @classmethod
    def set_location(cls, location: str) -> None:
        Session.set_location(location)
        cls._location = location

    @staticmethod
    def prepare_request(session: str) -> None:
        session = Session(session, from_sql=True)
        setattr(webapi.request, 'current_session', session)

    def add_sensors_data(self, data: dict) -> None:
        for session in self.alive_sessions:
            wanted = list(filter(lambda s: s in session.sensors, list(data.keys())))

            for sensor, values in data.items():
                if sensor in wanted:
                    session.add_sensor_data(sensor, values)

    @property
    def alive_sessions(self) -> iter:
        sessions = []

        sql = f'SELECT name FROM {self._tab.name} WHERE status = ?'
        results = self._tab.execute(sql, ('alive',))

        for name, in results:
            sessions.append(Session(name, from_sql=False))

        return sessions

    @property
    def sessions(self) -> dict:
        sql = f'SELECT name, creation, status, sensors FROM {self._tab.name}'

        results = self._tab.execute(sql)
        if results:
            d = {}
            for result in results:
                name, creation, status, sensors = result
                d[name] = {
                    'creation': creation,
                    'status': status,
                    'sensors': sensors
                }
            return d
        else:
            return {}


_manager = SessionsManager()

add_sensors_data = _manager.add_sensors_data
prepare_request = _manager.prepare_request


def get_sessions() -> dict:
    return _manager.sessions


def load() -> None:
    location = config.get_config('sessions')['Location']

    if not os.path.exists(f'{location}/'):
        os.mkdir(f'{location}')

    _manager.set_location(location)


def requires_session() -> callable:
    def wrapper(func) -> callable:
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            if webapi.request.current_session.status:
                result = func(*args, **kwargs)
            else:
                result = 'Sessions does not exist', 404
            return result

        return decorator
    return wrapper
