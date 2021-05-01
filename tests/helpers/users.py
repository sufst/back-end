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
from tests.helpers import privileges
from tests.plugins import db
import os
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


def create_user(username, password, privilege, meta):
    tab = Users()

    sql = f'SELECT username FROM {tab.name} WHERE username = ?'
    results = tab.execute(sql, (username,))

    if results:
        raise KeyError("User already exists")
    else:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        creation = time()

        sql = f'INSERT INTO {tab.name} (username, key, salt, creation, privilege, meta) VALUES (?,?,?,?,?,?)'
        try:
            tab.execute(sql, (username, key, salt, creation, int(privileges.from_string(privilege)), json.dumps(meta)))
        except Exception as err:
            print(repr(err))

