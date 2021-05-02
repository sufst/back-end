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
from src.plugins import db
from time import time
import json
import zipfile
from src.helpers import config
import weakref
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

    def __init__(self, name=None):
        self._name = name
        self._sensors = None
        self._meta = None
        self._tab = Sessions()
        self._status = None

    @property
    def name(self):
        return self._name

    @property
    def sensors(self):
        if self._sensors is None:
            sql = f'SELECT sensors FROM {self._tab.name} WHERE name = ?'
            result = self._tab.execute(sql, (self._name,))

            for sensors, in result:
                self._sensors = json.loads(sensors)

        return self._sensors

    @property
    def meta(self):
        if self._meta is None:
            with open(f'{self._location}/{self._name}/meta.json', 'r') as f:
                self._meta = json.load(f)

        return self._meta

    @property
    def is_exists(self):
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
    def status(self):
        if self._status is None:
            sql = f'SELECT status FROM {self._tab.name} WHERE name = ?'
            result = self._tab.execute(sql, (self._name,))

            for status, in result:
                self._status = status

        return self._status

    def create(self, sensors, meta):
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
                fieldnames = ['epoch', 'note']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

            for sensor in self._sensors:
                with open(f'{self._location}/{self._name}/{sensor}.csv', 'w', newline='') as f:
                    fieldnames = ['epoch', 'value']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
        else:
            raise KeyError('Session already exists')

    @classmethod
    def set_location(cls, location):
        cls._location = location

    def add_sensor_data(self, sensor, data):
        rows = list(map(lambda entry: {'epoch': entry['epoch'], 'value': entry['value']}, data))

        with open(f'{self._location}/{self._name}/{sensor}.csv', 'a', newline='') as f:
            fieldnames = ['epoch', 'value']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(rows)

    def _zip_session(self):
        if os.path.exists(f'{self._location}/{self._name}'):
            try:
                f_zip = zipfile.ZipFile(f'{self._location}/{self._name}/{self._name}.zip', 'x')
            except FileExistsError:
                print(f'{self._name}.zip already exists')
            else:
                for entry in os.listdir(f'{self._location}/{self._name}'):
                    if 'zip' not in entry:
                        f_zip.write(f'{self._location}/{self._name}/{entry}', f'{entry}')

                f_zip.close()

    @property
    def zip_path(self):
        if not os.path.exists(f'{self._location}/{self._name}/{self._name}.zip'):
            self._zip_session()

        return f'{self._location}/{self._name}/{self._name}.zip'

    def stop(self):
        sql = f'UPDATE {self._tab.name} SET status = ? WHERE name = ?'
        self._tab.execute(sql, ('dead', self._name, ))


class SessionsManager:
    _location = ''

    _mounted_session = None

    _sessions = []
    _sessions_proxy = {}

    def __init__(self):
        self._tab = Sessions()

        self._load_sessions()

    def _load_sessions(self):
        sql = f'SELECT name FROM {self._tab.name}'
        results = self._tab.execute(sql)

        for name, in results:
            self._sessions.append(Session(name))
            self._sessions_proxy[name] = weakref.proxy(self._sessions[-1])

    @classmethod
    def set_location(cls, location):
        Session.set_location(location)
        cls._location = location

    @property
    def mounted_session(self):
        return self._mounted_session

    def prepare_mount(self, session):
        if session not in self:
            self._sessions.append(Session(session))
            self._sessions_proxy[session] = weakref.proxy(self._sessions[-1])

        self._mounted_session = self._sessions_proxy[session]

    def cleanup_mount(self):
        if self._sessions[-1].status is None:
            self._sessions.pop(-1)

    def add_sensors_data(self, data):
        for session in self:
            wanted = list(filter(lambda s: s in session.sensors, list(data.keys())))

            for sensor, values in data.items():
                if sensor in wanted:
                    session.add_sensor_data(sensor, values)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self._sessions):
            result = self._sessions[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def __contains__(self, session):
        return session in self._sessions_proxy


_manager = SessionsManager()


def get_mounted_session():
    return _manager.mounted_session


def load():
    location = config.get_config('sessions')['Location']

    if not os.path.exists(f'{location}/'):
        os.mkdir(f'{location}')

    _manager.set_location(location)


def prepare_session(name):
    _manager.prepare_mount(name)


def add_sensors_data(data):
    _manager.add_sensors_data(data)


def requires_session():
    def wrapper(func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            if _manager.mounted_session.name is not None and _manager.mounted_session.is_exists:
                result = func(*args, **kwargs)
            else:
                result = 'Sessions does not exist', 404
            _manager.cleanup_mount()
            return result

        return decorator
    return wrapper
