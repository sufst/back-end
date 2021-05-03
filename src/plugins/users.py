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
import hashlib
from src.helpers import privileges
from src.plugins import webapi, db
import os
import werkzeug.security
import json
from time import time


class User:
    def __init__(self, username=None, key=None, salt=None, creation=None, privilege=None, meta=None):
        self.username = username
        self.key = key
        self.salt = salt
        self.meta = meta
        self.creation = creation
        self.privilege = privilege


class Users(db.Table):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'username TEXT NOT NULL',
        'key BLOB NOT NULL',
        'salt BLOB NOT NULL',
        'creation REAL NOT NULL',
        'privilege INTEGER NOT NULL',
        'meta TEXT NOT NULL'
    ]


class UsersManager:
    def __init__(self):
        self._tab = Users()

    def create(self, username, password, privilege, meta):
        sql = f'SELECT username FROM {self._tab.name} WHERE username = ?'
        results = self._tab.execute(sql, (username,))

        if results:
            raise KeyError("User already exists")
        else:
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
            creation = time()

            sql = f'INSERT INTO {self._tab.name} (username, key, salt, creation, privilege, meta) VALUES (?,?,?,?,?,?)'
            self._tab.execute(sql, (username, key, salt, creation, int(privileges.from_string(privilege)), json.dumps(meta)))

    def auth(self, username, password):
        if username == "anonymous":
            return webapi.create_access_token(identity=username, expires_delta=False)
        else:
            sql = f'SELECT key, salt FROM {self._tab.name} WHERE username = ?'
            results = self._tab.execute(sql, (username,))

            if not results:
                raise KeyError("User does not exist")
            else:
                key, salt = results[0]
                if werkzeug.security.safe_str_cmp(
                        hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000),
                        key):
                    return webapi.create_access_token(identity=username, expires_delta=False)
                else:
                    raise Exception('Password mismatch')

    def lookup_loader(self, _, payload):
        username = payload["sub"]

        if username == "anonymous":
            user = User(username='anonymous', privilege=privileges.anon)
        else:
            sql = f'SELECT username, key, salt, creation, privilege, meta FROM {self._tab.name} WHERE username = ?'
            results = self._tab.execute(sql, (username,))
            if results:
                name, key, salt, creation, privilege, meta = results[0]
                privilege = privileges.from_level(privilege)

                user = User(username, key, salt, creation, privilege, meta)
            else:
                user = None

        return user


_manager = UsersManager()

create_user = _manager.create
auth_user = _manager.auth


def load():
    try:
        _manager.create('intermediate_server', 'sufst', 'Basic', {})
        _manager.create('anonymous', 'anonymous', 'Anon', {})
    except KeyError:
        pass
    except Exception as err:
        print(err)

    webapi.jwt.user_lookup_loader(_manager.lookup_loader)
