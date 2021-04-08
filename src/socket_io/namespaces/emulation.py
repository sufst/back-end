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
import flask_jwt_extended
import json
from socket_io.namespace import Namespace


class Emulation(Namespace):
    @flask_jwt_extended.jwt_required()
    def on_meta(self, meta):
        meta = json.loads(meta)

        self._handle_meta(meta)
        self._schedule_data_emit()

    @flask_jwt_extended.jwt_required()
    def on_data(self, data):
        data = json.loads(data)
        self._handle_data(data)
