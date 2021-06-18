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
from src.helpers import privileges, departments
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
        'department INTEGER NOT NULL',
        'meta TEXT NOT NULL'
    ]


class User:
    _tab = Users()

    def __init__(self, username: str = None, uid: int = None, privilege: str = None, department: str = None):
        self.uid = uid
        self.username = username
        self.key = None
        self.salt = None
        self.meta = {}
        self.creation = None
        self.privilege = privilege
        self.department = department

    def update_username(self, new: str) -> None:
        sql = f'UPDATE {self._tab.name} SET username = ? WHERE id = ?'
        self._tab.execute(sql, (new, self.uid))
        self.username = new

    def update_password(self, new: str) -> None:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", new.encode("utf-8"), salt, 100000)

        sql = f'UPDATE {self._tab.name} SET salt = ? WHERE id = ?'
        self._tab.execute(sql, (new, self.uid))
        self.salt = salt

        sql = f'UPDATE {self._tab.name} SET key = ? WHERE id = ?'
        self._tab.execute(sql, (new, self.uid))
        self.key = key

    def update_meta(self, key: str, value: any) -> None:
        self.meta.update({key, value})
        sql = f'UPDATE {self._tab.name} SET meta = ? WHERE id = ?'
        self._tab.execute(sql, (self.meta, self.uid))

    def update_privilege(self, new: str) -> None:
        sql = f'UPDATE {self._tab.name} SET privilege = ? WHERE id = ?'
        self._tab.execute(sql, (int(privileges.from_string(new)), self.uid))
        self.privilege = new

    def update_department(self, new: str) -> None: 
        sql = f'UPDATE {self._tab.name} SET department = ? WHERE id = ?'
        self._tab.execute(sql, (int(departments.from_string(new)), self.uid))
        self.department = new

    def _from_sql(self, sql: str, args: tuple) -> object:
        results = self._tab.execute(sql, args)
        if results:
            uid, username, key, salt, creation, privilege, department, meta = results[0]
            privilege = privileges.from_level(privilege)
            department = departments.from_number(department)

            self.uid = uid
            self.username = username
            self.key = key
            self.salt = salt
            self.creation = creation
            self.privilege = privilege
            self.department = department
            self.meta = meta

        return self

    def from_uid(self, uid: int) -> object:
        sql = f'SELECT id, username, key, salt, creation, privilege, department, meta FROM {self._tab.name} WHERE id = ?'
        return self._from_sql(sql, (uid,))

    def from_username(self) -> object:
        sql = f'SELECT id, username, key, salt, creation, privilege, department, meta FROM {self._tab.name} WHERE username = ?'
        return self._from_sql(sql, (self.username,))

    def create(self, password: str, privilege: str, department: str, meta: dict) -> None:
        sql = f'SELECT id FROM {self._tab.name} WHERE username = ?'
        results = self._tab.execute(sql, (self.username,))

        if results:
            raise KeyError("User already exists")
        else:
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
            creation = time()

            sql = f'INSERT INTO {self._tab.name} (username, key, salt, creation, privilege, department, meta) VALUES (?,?,?,?,?,?,?)'
            self._tab.execute(sql, (self.username, key, salt, creation,
                                    int(privileges.from_string(privilege)), int(departments.from_string(department)), json.dumps(meta)))

            sql = f'SELECT id FROM {self._tab.name} WHERE username = ?'
            results = self._tab.execute(sql, (self.username,))

            self.uid, = results[0]
            self.key = key
            self.salt = salt
            self.creation = creation
            self.privilege = privilege
            self.department = department
            self.meta = meta

    def auth(self, password: str) -> str:
        if self.username == 'anonymous':
            return webapi.create_access_token(identity=0, expires_delta=False)
        else:
            if not self.key or not self.salt:
                raise KeyError("User does not exist")
            else:
                if werkzeug.security.safe_str_cmp(
                        hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), self.salt, 100000),
                        self.key):
                    return webapi.create_access_token(identity=self.uid, expires_delta=False)
                else:
                    raise KeyError('Password mismatch')


class UsersManager:
    def __init__(self):
        self._tab = Users()

    @staticmethod
    def prepare_webapi_request(username: str) -> None:
        setattr(webapi.request, 'wanted_user', User(username=username).from_username())

    @staticmethod
    def lookup_loader(_: dict, payload: dict) -> User:
        uid = payload["sub"]

        if uid == 0:
            user = User(username='anonymous', uid=0, privilege=privileges.anon)
        else:
            user = User().from_uid(uid)

        return user

    def fetch_all_users(self):
        sql = f'SELECT id, username, creation, privilege, department, meta FROM {self._tab.name} WHERE id != 1 AND id != 2 AND id != 3'
        # sql = f'SELECT id, username, creation, privilege, department, meta FROM {self._tab.name}'
        result = self._tab.execute(sql)

        if len(result) > 0:
            return result
        else:
            return []


_manager = UsersManager()

prepare_request = _manager.prepare_webapi_request
fetch_all_users = _manager.fetch_all_users


def create_user(username: str, password: str, privilege: str, department: str, meta: dict) -> None:
    User(username).create(password, privilege, department, meta)


# TODO: Remove Dummy Admin User - Here Just for Development
def load() -> None:
    try:
        create_user('intermediate_server', 'sufst', 'Basic', 'NON SPECIFIED', {})
        create_user('anonymous', 'anonymous', 'Anon', 'NON SPECIFIED', {})
        create_user('admin', 'admin', 'Admin', 'Electronics', {})
    except KeyError:
        pass
    except Exception as err:
        print(err)

    webapi.jwt.user_lookup_loader(_manager.lookup_loader)
