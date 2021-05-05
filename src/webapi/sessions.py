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
from src.plugins import webapi, sessions
from src.helpers import privileges
import json


def _on_sessions_get_zip() -> str or tuple:
    session = webapi.request.current_session

    try:
        with open(session.zip_path, 'rb') as f:
            c = f.read()
            rsp = webapi.Response(c)
            rsp.headers['Content-Type'] = 'application/zip'
            rsp.headers['Content-Disposition'] = f'attachment; filename="{session.name}.zip"'
            rsp.headers['Content-Length'] = len(c)

        return rsp
    except FileNotFoundError as err:
        return repr(err), 404


def _on_session_get_json() -> str or tuple:
    session = webapi.request.current_session

    try:
        d = {
            'meta': session.meta,
            'notes': session.notes,
            'data': session.data
        }
        rsp = webapi.Response(json.dumps(d))
        rsp.headers['Content-Type'] = 'application/json'

        return rsp
    except Exception as err:
        return repr(err), 500


@sessions.requires_session()
def _on_sessions_get() -> str or tuple:
    content_type = webapi.request.headers.get('Content-Type')

    handlers = {
        'application/zip': lambda: _on_sessions_get_zip(),
        'application/json': lambda: _on_session_get_json()
    }

    args = list(handlers.keys())

    if content_type not in args:
        return 'Invalid Content-Type', 400

    return handlers[content_type]()


@privileges.privilege_required(privileges.basic)
def _on_sessions_post() -> str or tuple:
    data = webapi.request.get_json()

    fields = [
        'sensors',
        'meta'
    ]

    if not set(fields) == set(data.keys()):
        return 'Invalid session args', 400

    sensors = data['sensors']
    meta = data['meta']

    session = webapi.request.current_session

    try:
        session.create(sensors, meta)
    except Exception as err:
        return repr(err), 409
    else:
        return json.dumps({'status': session.status}), 200


def _on_sessions_patch_status(status: str) -> None:
    session = webapi.request.current_session

    if status == 'dead':
        session.stop()


@privileges.privilege_required(privileges.basic)
@sessions.requires_session()
def _on_sessions_patch() -> str or tuple:
    data = webapi.request.get_json()

    handlers = {
        'status': lambda s: _on_sessions_patch_status(s)
    }

    args = list(handlers.keys())

    if not list(filter(lambda k: k in args, list(data.keys()))):
        return 'No valid arg', 400

    for key, value in data.items():
        if key in handlers:
            handlers[key](value)

    return '', 200


def _on_sessions_put_note(note: str) -> None:
    session = webapi.request.current_session

    session.add_note(note)


@privileges.privilege_required(privileges.basic)
@sessions.requires_session()
def _on_sessions_put() -> str or tuple:
    data = webapi.request.get_json()

    handlers = {
        'note': lambda n: _on_sessions_put_note(n)
    }

    args = list(handlers.keys())

    if not list(filter(lambda k: k in args, list(data.keys()))):
        return 'No valid arg', 400

    for key, value in data.items():
        if key in handlers:
            handlers[key](value)

    return '', 200


@webapi.endpoint('/sessions/<name>', methods=['GET', 'POST', 'PATCH', 'PUT'])
def _sessions(name: str) -> str or tuple:
    sessions.prepare_request(name)

    return webapi.route({
        'GET': lambda: _on_sessions_get(),
        'POST': lambda: _on_sessions_post(),
        'PATCH': lambda: _on_sessions_patch(),
        'PUT': lambda: _on_sessions_put()
    })
