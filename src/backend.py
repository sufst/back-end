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
import namespaces.emulation
import flask_login
import common.configuration


class Backend:
    def __init__(self):
        config_manager = common.configuration.get_configuration_manager()
        config_manager.init_configuration("../config.xml")

        database_config = config_manager.configuration["database"]

        self._app = flask.Flask(__name__)
        self._app.config["JWT_SECRET_KEY"] = os.urandom(16)
        self._app.config["SECRET_KEY"] = os.urandom(16)
        self._app.config["MONGO_URI"] = database_config["mongodb_url"]

        self._socket_io = flask_socketio.SocketIO(self._app, cors_allowed_origins="*", manage_session=False)
        self._jwt = flask_jwt_extended.JWTManager(self._app)
        self._mongo = flask_pymongo.PyMongo(self._app)
        self._login_manager = flask_login.LoginManager(self._app)
        self._login_manager.init_app(self._app)
        self._api = flask_restful.Api(self._app)

        self._login_manager.request_loader(common.user_management.get_user_management().request_loader)
        flask_cors.CORS(self._app)
        common.database.get_database_manager().init_db(mongo_db=self._mongo)

        self._api.add_resource(resources.users.Users, "/users/<string:username>")
        self._api.add_resource(resources.login.Login, "/login")

        self._socket_io.on_namespace(namespaces.frontend.FrontEnd("/frontend"))
        self._socket_io.on_namespace(namespaces.emulation.Emulation("/emulation"))

    def serve_forever(self):
        config_manager = common.configuration.get_configuration_manager()

        server_config = config_manager.configuration["server"]

        print(f"Hosting on {server_config['ip']}:{server_config['port']}")

        self._socket_io.run(self._app, host=server_config["ip"], port=server_config["port"],
                            certfile=server_config["fullchain"], keyfile=server_config["privkey"])

