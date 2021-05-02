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


@sessions.requires_session()
def _on_sessions_get():
    session = sessions.get_mounted_session()

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


@privileges.privilege_required(privileges.basic)
def _on_sessions_post():
    data = webapi.request.get_json()

    sensors = data['sensors']
    meta = data['meta']

    session = sessions.get_mounted_session()

    try:
        session.create(sensors, meta)
    except Exception as err:
        return repr(err), 409
    else:
        return json.dumps({'status': session.status}), 200


@privileges.privilege_required(privileges.basic)
@sessions.requires_session()
def _on_sessions_patch():
    data = webapi.request.get_json()

    session = sessions.get_mounted_session()

    if 'status' in data:
        if data['status'] == 'dead':
            session.stop()
        return '', 200
    else:
        return 'No valid key to patch', 400


# @privileges.privilege_required(privileges.basic)
# @sessions.requires_session()
# def _on_sessions_put():
#     data = webapi.request.get_json()
#
#     if 'note' in data:
#


@webapi.endpoint('/sessions/<name>', methods=['GET', 'POST', 'PATCH'])
def _sessions(name):
    sessions.prepare_session(name)

    return webapi.route({
        'GET': _on_sessions_get,
        'POST': _on_sessions_post,
        'PATCH': _on_sessions_patch
    })
