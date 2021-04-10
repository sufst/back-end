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
from configuration import config
from database import database
from users import users
from flask_cors import CORS
from flask import Flask
from rest import rest
from socket_io import socket_io
import flask_jwt_extended
import os
from scheduler import scheduler

__all__ = ["app"]


class App:
    @staticmethod
    def run():
        print("Starting app")
        config.start()
        scheduler.start()

        flask = Flask(__name__)
        CORS(flask)
        flask.config["JWT_SECRET_KEY"] = os.urandom(16)
        flask.config["SECRET_KEY"] = os.urandom(16)

        jwt = flask_jwt_extended.JWTManager(flask)
        jwt.user_lookup_loader(users.user_lookup_loader)

        rest.init(flask)
        socket_io.init(flask)

        database.start()
        print("Started app")

        socket_io.run(flask, host="0.0.0.0", port=5000)


app = App()
