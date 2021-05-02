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
from src.plugins import sio, sessions, webapi
from src.helpers import privileges
from time import time
import json
import pickle


@sio.sio.on('connect', '/car')
@privileges.privilege_required(privileges.anon)
def on_connect():
    tab = sio.Meta()

    sql = f'SELECT meta FROM {tab.name} ORDER BY id DESC LIMIT 1'
    results = tab.execute(sql)

    room = webapi.request.sid
    if results:
        meta = results[0]
        sio.sio.emit('meta', meta, namespace='/car', room=room)


@sio.sio.on('disconnect', '/car')
@privileges.privilege_required(privileges.anon)
def on_disconnect():
    user = webapi.current_user


@sio.sio.on('meta', '/car')
@privileges.privilege_required(privileges.anon)
def on_meta(meta):
    tab = sio.Meta()

    sql = f'INSERT INTO {tab.name} (creation, meta) VALUES (?,?)'
    tab.execute(sql, (time(), meta))

    sio.sio.emit('meta', meta, namespace='/car')


@sio.sio.on('data', '/car')
@privileges.privilege_required(privileges.anon)
def on_data(data):
    tab = sio.Stage()

    data = json.loads(data)
    sql = f'INSERT INTO {tab.name} (data) VALUES (?)'
    tab.execute(sql, (pickle.dumps(data),))

    sessions.add_sensors_data(data)
