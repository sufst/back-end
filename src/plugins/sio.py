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
from helpers import flask, config, db, scheduler
from time import time
import json
from plugins import session
import pickle

sio = flask_socketio.SocketIO(cors_allowed_origins="*", manage_session=False)


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


def run():
    host = config.get_config('server')['Host']
    port = config.get_config('server').getint('Port')
    print(f'Serving on {host}:{port}')

    sio.run(flask.app, host=host, port=port)


@scheduler.schedule_job(scheduler.IntervalTrigger(seconds=config.get_config('sio').getfloat('EmitInterval')))
def _emit_job():
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


@sio.on('connect', '/car')
@flask.jwt_required()
def on_connect():
    user = flask.current_user
    print(f"{user.username} connected to /car")

    if not user.username == 'intermediate-server':
        tab = Meta()

        sql = f'SELECT meta FROM {tab.name} ORDER BY id DESC LIMIT 1'
        results = tab.execute(sql)

        room = flask.request.sid
        if results:
            meta = results[0]
            sio.emit('meta', meta, namespace='/car', room=room)


@sio.on('disconnect', '/car')
@flask.jwt_required()
def on_disconnect():
    user = flask.current_user
    print(f"{user.username} disconnected from /car")


@sio.on('meta', '/car')
@flask.jwt_required()
def on_meta(meta):
    user = flask.current_user

    print(f"{user.username} meta {meta}")
    tab = Meta()

    sql = f'INSERT INTO {tab.name} (creation, meta) VALUES (?,?)'
    tab.execute(sql, (time(), meta))


@sio.on('data', '/car')
@flask.jwt_required()
def on_data(data):
    tab = Stage()

    data = json.loads(data)
    sql = f'INSERT INTO {tab.name} (data) VALUES (?)'
    tab.execute(sql, (pickle.dumps(data),))

    session.write_sensors(data)


sio.init_app(flask.app)
