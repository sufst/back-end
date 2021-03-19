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

import logging
import xml.etree.ElementTree
import flask
import ssl
import flask_cors
import resources.users
import resources.login
import flask_restful
import flaskext.mysql
import common.database
import common.user_management
import flask_jwt_extended
import os

app = flask.Flask(__name__)
flask_cors.CORS(app)
api = flask_restful.Api(app)
mysql = flaskext.mysql.MySQL()
mysql.init_app(app)
app.config["JWT_SECRET_KEY"] = os.urandom(16)

common.database.Database().instance()
common.user_management.UserManagement().instance()

jwt = flask_jwt_extended.JWTManager(app)


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('domain.crt', 'domain.key')

api.add_resource(resources.users.Users, "/users/<string:username>")
api.add_resource(resources.login.Login, "/login")

app.run(ssl_context=ssl_context)
