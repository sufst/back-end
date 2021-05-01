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


class Sessions(db.Table):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'name TEXT NOT NULL',
        'creation REAL NOT NULL',
        'status TEXT NOT NULL',
        'sensors TEXT NOT NULL',
        'notes TEXT NOT NULL',
        'meta TEXT NOT NULL'
    ]


_location = ''


def load():
    global _location
    _location = config.get_config('sessions')['Location']

    if not os.path.exists(f'{_location}/'):
        os.mkdir(f'{_location}')


def new_session(name, sensors, meta):
    tab = Sessions()

    sql = f'SELECT name FROM {tab.name} WHERE name = ?'
    results = tab.execute(sql, (name,))

    if results:
        raise KeyError('Session already exists')
    else:
        if not os.path.exists(f'{_location}/{name}/'):
            os.mkdir(f'{_location}/{name}/')

        sql = f'INSERT INTO {tab.name} (name, creation, status, sensors, notes, meta) VALUES (?,?,?,?,?,?)'
        tab.execute(sql, (name, time(), 'alive', json.dumps(sensors), json.dumps({}), json.dumps(meta)))

        for sensor in sensors:
            with open(f'{_location}/{name}/{sensor}.csv', 'w', newline='') as f:
                fieldnames = ['epoch', 'value']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()


def write_sensors(data):
    tab = Sessions()

    sql = f'SELECT name FROM {tab.name} WHERE status = ?'
    sessions = tab.execute(sql, ('alive',))

    for session, in sessions:
        sql = f'SELECT sensors FROM {tab.name} WHERE name = ?'
        result = tab.execute(sql, (session,))

        for sensors, in result:
            sensors = json.loads(sensors)

            wanted = list(filter(lambda sensor: sensor in sensors, sensors))

            for s in wanted:
                rows = list(map(lambda entry: {'epoch': entry['epoch'], 'value': entry['value']}, data[s]))

                with open(f'{_location}/{session}/{s}.csv', 'a', newline='') as f:
                    fieldnames = ['epoch', 'value']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerows(rows)


def _zip_session(name):
    if os.path.exists(f'{_location}/{name}'):
        try:
            f_zip = zipfile.ZipFile(f'{_location}/{name}/{name}.zip', 'x')
        except FileExistsError:
            print(f'{name}.zip already exists')
        else:
            for entry in os.listdir(f'{_location}/{name}'):
                f_name, f_ext = entry.split('.')
                if f_ext == 'csv':
                    f_zip.write(f'{_location}/{name}/{f_name}.csv', f'{f_name}.csv')

            f_zip.close()


def get_zip_file(name):
    if os.path.exists(f'{_location}/{name}'):
        if not os.path.exists(f'{_location}/{name}/{name}.zip'):
            _zip_session(name)

        return f'{_location}/{name}/{name}.zip'
    else:
        raise FileExistsError(f'{name} does not exist')


def end_session(name):
    tab = Sessions()

    sql = f'UPDATE {tab.name} SET status = ? WHERE name = ?'
    tab.execute(sql, ('dead', name, ))
