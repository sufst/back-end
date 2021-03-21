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
import flask_login


class User(flask_login.UserMixin):
    def __init__(self):
        self.id = None
        self.username = None
        self.key = None
        self.salt = None
        self.authenticated = False
        self.active = False
        self.anonymous = False

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_anonymous(self):
        return self.anonymous

    def from_record(self, record: dict):
        if record is None:
            return None

        self.id = str(record["_id"])
        self.username = record["username"]
        self.key = record["key"]
        self.salt = record["salt"]

        return self

    def from_values(self, username: str, key: bytes, salt: bytes):
        self.username = username
        self.key = key
        self.salt = salt

        return self

    def get_record(self):
        return {
            "username": self.username,
            "key": self.key,
            "salt": self.salt
        }

