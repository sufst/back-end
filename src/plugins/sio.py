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
from src.helpers import config
import json
from src.plugins import scheduler, webapi, db
import pickle
import os
import importlib


class Meta(db.Table):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'creation REAL NOT NULL',
        'meta BLOB NOT NULL'
    ]


class Stage(db.StageTable):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'data TEXT NOT NULL'
    ]


sio = flask_socketio.SocketIO(cors_allowed_origins="*", manage_session=False)


def run() -> None:
    host = config.get_config('server')['Host']
    port = config.get_config('server').getint('Port')

    sio.run(webapi.app, host=host, port=port)


def stop() -> None:
    sio.stop()


def load() -> None:
    sio.init_app(webapi.app)

    for f in os.listdir('./src/namespaces'):
        if f not in '__init__':
            importlib.import_module(f'src.namespaces.{f.split(".")[0]}')

    scheduler.add_job(_car_data_emit, scheduler.IntervalTrigger(
        seconds=config.get_config('sio').getfloat('EmitInterval')))


def _car_data_emit() -> None:
    tab = Stage()

    sql = f'SELECT id, data FROM {tab.name} ORDER BY id ASC'
    results = tab.execute(sql)

    if results:
        eid = list(map(lambda result: result[0], results))

        sensors = {}
        for _, data in results:
            data = pickle.loads(data)

            for sensor, values in data.items():
                if sensor not in sensors:
                    sensors[sensor] = []

                sensors[sensor].extend(values)

        sio.emit('data', json.dumps(sensors), namespace='/car')

        sql = f'DELETE FROM {tab.name} WHERE id IN ({",".join(list(map(lambda _: "?", eid)))})'
        tab.execute(sql, tuple(eid))
