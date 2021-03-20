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
import namespaces.frontend
import flask_login

app = flask.Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.urandom(16)
app.config["SECRET_KEY"] = os.urandom(16)
app.config["MONGO_URI"] = "mongodb://localhost:27017/local"

socketIO = flask_socketio.SocketIO(app, cors_allowed_origins="*", manage_session=False)
jwt = flask_jwt_extended.JWTManager(app)
mongo = flask_pymongo.PyMongo(app)
loginManager = flask_login.LoginManager(app)
loginManager.init_app(app)
api = flask_restful.Api(app)


loginManager.request_loader(common.user_management.UserManagement().instance().request_loader)
flask_cors.CORS(app)
common.database.Database().init_db(mongo_db=mongo)

api.add_resource(resources.users.Users, "/users/<string:username>")
api.add_resource(resources.login.Login, "/login")

socketIO.on_namespace(namespaces.frontend.FrontEnd("/frontend"))

socketIO.run(app, host="0.0.0.0", port=5000, certfile='domain.crt', keyfile='domain.key')

