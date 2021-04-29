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
from helpers import db
from time import time
import json
import pickle


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


def load():
    if not os.path.exists('sessions/'):
        os.mkdir('sessions/')

    try:
        new_session('test', ['rpm'], json.dumps({'awesome': True}))
    except Exception as e:
        print(e)


def new_session(name, sensors, meta):
    tab = Sessions()

    sql = f'SELECT name FROM {tab.name} WHERE name = ?'
    results = tab.execute(sql, (name,))

    if results:
        raise KeyError('Session already exists')
    else:
        if not os.path.exists(f'sessions/{name}/'):
            os.mkdir(f'sessions/{name}/')

        sql = f'INSERT INTO {tab.name} (name, creation, status, sensors, meta) VALUES (?,?,?,?,?)'
        tab.execute(sql, (name, time(), 'alive', json.dumps(sensors), meta))

        for sensor in sensors:
            with open(f'sessions/{name}/{sensor}.csv', 'w', newline='') as f:
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

                with open(f'sessions/{session}/{s}.csv', 'a', newline='') as f:
                    fieldnames = ['epoch', 'value']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerows(rows)


def end_session(name):
    tab = Sessions()

    sql = f'UPDATE {tab.name} SET status = dead WHERE name = ?'
    tab.execute(sql, (name, ))
