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
import flask_cors
import resources.users
import resources.login
import flask_restful
import common.database
import common.user_management
import flask_jwt_extended
import os
import flask_socketio
import flask_pymongo


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
flask_cors.CORS(app)
api = flask_restful.Api(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/local"
app.config["JWT_SECRET_KEY"] = os.urandom(16)
app.config["SECRET_KEY"] = os.urandom(16)

socket_io = flask_socketio.SocketIO(app, cors_allowed_origins="*")
jwt = flask_jwt_extended.JWTManager(app)

mongo = flask_pymongo.PyMongo(app)

common.database.Database().init_db(mongo_db=mongo)

api.add_resource(resources.users.Users, "/users/<string:username>")
api.add_resource(resources.login.Login, "/login")


@socket_io.on('connect')
def test_connect():
    print("connect")


@socket_io.on('message')
def my_message(data):
    print('message received with ', data)


@socket_io.on('disconnect')
def disconnect():
    print('disconnected from client')


socket_io.run(app, host="0.0.0.0", port=5000, certfile='domain.crt', keyfile='domain.key')

