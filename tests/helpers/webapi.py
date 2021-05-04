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
from urllib import request
from tests.helpers import config
import json


def build_request(end_point, method, data=None, token=None, content_type=None):
    host = 'localhost'
    port = config.get_config('server')["Port"]

    url = f'http://{host}:{port}/{end_point}'

    if data:
        data = json.dumps(data).encode('utf-8')

    headers = {}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if content_type:
        headers['Content-Type'] = content_type

    return request.Request(url, data=data, headers=headers, method=method)
