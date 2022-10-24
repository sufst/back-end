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

import flask
import flask_jwt_extended
import flask_cors
import os
import importlib
from server import projectPath


app = flask.Flask(__name__)

flask_cors.CORS(app)
app.config['JWT_SECRET_KEY'] = os.urandom(16)
app.config['SECRET_KEY'] = os.urandom(16)
jwt = flask_jwt_extended.JWTManager(app)

endpoint = app.route
request = flask.request
current_user = flask_jwt_extended.current_user
jwt_required = flask_jwt_extended.jwt_required
create_access_token = flask_jwt_extended.create_access_token
Response = flask.Response


def load() -> None:
    for f in os.listdir(projectPath + '/src/webapi'):
        if '__' not in f:
            importlib.import_module(f'src.webapi.{f.split(".")[0]}')


def route(handlers: dict, *args, **kwargs) -> tuple:
    method = flask.request.method

    if method in handlers:
        return handlers[method](*args, **kwargs)
    else:
        return None, 404
