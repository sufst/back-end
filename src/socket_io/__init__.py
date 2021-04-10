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
import flask_socketio
from socket_io.namespaces import Emulation, Car

__all__ = ["socket_io"]


class SocketIO:
    sio = None

    def init(self, app):
        print("Starting socket.io")
        self.sio = flask_socketio.SocketIO(app, cors_allowed_origins="*", manage_session=False)
        self.sio.init_app(app)
        self.sio.on_namespace(Emulation("/emulation"))
        self.sio.on_namespace(Car("/car"))
        print("Started socket.io")

    def run(self, *args, **kwargs):
        self.sio.run(*args, **kwargs)


socket_io = SocketIO()
