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
from helpers import db, flask, config
from time import time

sio = flask_socketio.SocketIO(cors_allowed_origins="*", manage_session=False)


class Meta(db.Table):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'creation REAL NOT NULL',
        'meta TEXT NOT NULL'
    ]


class Stage(db.StageTable):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'data BLOB NOT NULL'
    ]


def load():
    pass


def run():
    host = config.config['server']['Host']
    port = config.config['server'].getint('Port')
    print(f'Serving on {host}:{port}')

    sio.run(flask.app, host=host, port=port)


@sio.on('connect', '/car')
@flask.jwt_required()
def on_connect():
    user = flask.current_user
    print(f"{user.username} connected to /car")

    tab = Meta()

    with tab as cur:
        cur.execute(f'SELECT meta FROM {tab.name} ORDER BY id DESC LIMIT 1')
        meta = cur.fetchone()

    if meta is not None:
        sio.emit('meta', meta, room=flask.request.sid)


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

    with tab as cur:
        cur.execute(f'INSERT INTO {tab.name} (creation, meta) VALUES (?,?)', (time(), meta))


@sio.on('data', '/car')
@flask.jwt_required()
def on_data(data):
    tab = Stage()

    with tab as cur:
        cur.execute(f'INSERT INTO {tab.name} (data) VALUES (?)', (data,))


sio.init_app(flask.app)
