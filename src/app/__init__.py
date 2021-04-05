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
from namespaces import Emulation, Car
from configuration import config
from resources import Login, User
from database import database
from users import usersManager
import flask
import flask_cors
import flask_restful
import flask_jwt_extended
import os
import flask_socketio
from scheduler import scheduler

__all__ = ["app", "sio"]

print("Starting app")
config.start()
scheduler.start()

app = flask.Flask(__name__)
flask_cors.CORS(app)
app.config["JWT_SECRET_KEY"] = os.urandom(16)
app.config["SECRET_KEY"] = os.urandom(16)

sio = flask_socketio.SocketIO(app, cors_allowed_origins="*", manage_session=False)
sio.init_app(app)
sio.on_namespace(Emulation("/emulation"))
sio.on_namespace(Car("/car"))


jwt = flask_jwt_extended.JWTManager(app)
jwt.user_lookup_loader(usersManager.user_lookup_loader)


api = flask_restful.Api(app)
api.add_resource(User, "/user")
api.add_resource(Login, "/login")

database.start()
print("Started app")
