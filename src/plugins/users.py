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


class User:
    _tab = Users()

    def __init__(self, username=None, uid=None, privilege=None):
        self.uid = uid
        self.username = username
        self.key = None
        self.salt = None
        self.meta = {}
        self.creation = None
        self.privilege = privilege

    def update_username(self, new):
        sql = f'UPDATE {self._tab.name} SET username = ? WHERE id = ?'
        self._tab.execute(sql, (new, self.uid))
        self.username = new

    def update_password(self, new):
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", new.encode("utf-8"), salt, 100000)

        sql = f'UPDATE {self._tab.name} SET salt = ? WHERE id = ?'
        self._tab.execute(sql, (new, self.uid))
        self.salt = salt

        sql = f'UPDATE {self._tab.name} SET key = ? WHERE id = ?'
        self._tab.execute(sql, (new, self.uid))
        self.key = key

    def update_meta(self, key, value):
        self.meta.update({key, value})
        sql = f'UPDATE {self._tab.name} SET meta = ? WHERE id = ?'
        self._tab.execute(sql, (self.meta, self.uid))

    def update_privilege(self, new):
        sql = f'UPDATE {self._tab.name} SET privilege = ? WHERE id = ?'
        self._tab.execute(sql, (int(privileges.from_string(new)), self.uid))
        self.privilege = new

    def _from_sql(self, sql, args):
        results = self._tab.execute(sql, args)
        if results:
            uid, username, key, salt, creation, privilege, meta = results[0]
            privilege = privileges.from_level(privilege)

            self.uid = uid
            self.username = username
            self.key = key
            self.salt = salt
            self.creation = creation
            self.privilege = privilege
            self.meta = meta

        return self

    def from_uid(self, uid):
        sql = f'SELECT id, username, key, salt, creation, privilege, meta FROM {self._tab.name} WHERE id = ?'
        return self._from_sql(sql, (uid,))

    def from_username(self):
        sql = f'SELECT id, username, key, salt, creation, privilege, meta FROM {self._tab.name} WHERE username = ?'
        return self._from_sql(sql, (self.username,))

    def create(self, password, privilege, meta):
        sql = f'SELECT id FROM {self._tab.name} WHERE username = ?'
        results = self._tab.execute(sql, (self.username,))

        if results:
            raise KeyError("User already exists")
        else:
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
            creation = time()

            sql = f'INSERT INTO {self._tab.name} (username, key, salt, creation, privilege, meta) VALUES (?,?,?,?,?,?)'
            self._tab.execute(sql, (self.username, key, salt, creation,
                                    int(privileges.from_string(privilege)), json.dumps(meta)))

            sql = f'SELECT id FROM {self._tab.name} WHERE username = ?'
            results = self._tab.execute(sql, (self.username,))

            self.uid, = results[0]
            self.key = key
            self.salt = salt
            self.creation = creation
            self.privilege = privilege
            self.meta = meta

    def auth(self, password):
        if self.username == 'anonymous':
            return webapi.create_access_token(identity=0, expires_delta=False)
        else:
            if self.username is None:
                raise KeyError("User does not exist")
            else:
                if werkzeug.security.safe_str_cmp(
                        hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), self.salt, 100000),
                        self.key):
                    return webapi.create_access_token(identity=self.uid, expires_delta=False)
                else:
                    raise Exception('Password mismatch')


class UsersManager:
    def __init__(self):
        self._tab = Users()

    @staticmethod
    def prepare_webapi_request(username):
        setattr(webapi.request, 'wanted_user', User(username=username).from_username())

    @staticmethod
    def lookup_loader(_, payload):
        uid = payload["sub"]

        if uid == 0:
            user = User(username='anonymous', uid=0, privilege=privileges.anon)
        else:
            user = User().from_uid(uid)

        return user


_manager = UsersManager()

prepare_request = _manager.prepare_webapi_request


def create_user(username, password, privilege, meta):
    User(username).create(password, privilege, meta)


def load():
    try:
        create_user('intermediate_server', 'sufst', 'Basic', {})
        create_user('anonymous', 'anonymous', 'Anon', {})
    except KeyError:
        pass
    except Exception as err:
        print(err)

    webapi.jwt.user_lookup_loader(_manager.lookup_loader)