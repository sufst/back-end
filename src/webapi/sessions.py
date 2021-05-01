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
from src.plugins import webapi, session
from src.helpers import privileges
import json


def _on_sessions_get(name):
    try:
        with open(session.get_zip_file(name), 'rb') as f:
            c = f.read()
            rsp = webapi.Response(c)
            rsp.headers['Content-Type'] = 'application/zip'
            rsp.headers['Content-Disposition'] = f'attachment; filename="{name}.zip"'
            rsp.headers['Content-Length'] = len(c)

        return rsp
    except FileExistsError as err:
        return repr(err), 404


@privileges.privilege_required(privileges.basic)
def _on_sessions_post(name):
    data = webapi.request.get_json()

    sensors = data['sensors']
    meta = data['meta']

    try:
        session.new_session(name, sensors, meta)
    except Exception as err:
        return repr(err), 409
    else:
        return json.dumps({'status': 'alive'}), 200


@privileges.privilege_required(privileges.basic)
def _on_sessions_patch(name):
    data = webapi.request.get_json()

    if 'status' in data:
        if data['status'] == 'dead':
            session.end_session(name)
        return '', 200
    else:
        return 'No valid key to patch', 400


@webapi.endpoint('/sessions/<name>', methods=['GET', 'POST', 'PATCH'])
def sessions(name):
    return webapi.route({
        'GET': lambda n: _on_sessions_get(n),
        'POST': lambda n: _on_sessions_post(n),
        'PATCH': lambda n: _on_sessions_patch(n)
    }, name)
