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
from helpers import flask, db
import os
import werkzeug.security
import json


class User:
    def __init__(self, username=None, key=None, salt=None, meta=None):
        self.username = username
        self.key = key
        self.salt = salt
        self.meta = meta

        self.authenticated = False
        self.anonymous = False


class Users(db.Table):
    columns = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'username TEXT NOT NULL',
        'key BLOB NOT NULL',
        'salt BLOB NOT NULL',
        'meta TEXT NOT NULL'
    ]


def create_user(username, password, meta):
    print(f"Attempting user create {username}")
    tab = Users()

    sql = f'SELECT username FROM {tab.name} WHERE username = ?'
    results = tab.execute(sql, (username,))

    if results:
        raise KeyError("User already exists")
    else:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)

        sql = f'INSERT INTO {tab.name} (username, key, salt, meta) VALUES (?,?,?,?)'
        tab.execute(sql, (username, key, salt, json.dumps(meta)))


def auth_user(username, password):
    if username == "anonymous":
        return flask.create_access_token(identity=username, expires_delta=False)
    else:
        tab = Users()

        sql = f'SELECT key, salt FROM {tab.name} WHERE username = ?'
        results = tab.execute(sql, (username,))

        if not results:
            raise KeyError("User does not exist")
        else:
            key, salt = results[0]
            if werkzeug.security.safe_str_cmp(
                    hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000),
                    key):
                return flask.create_access_token(identity=username, expires_delta=False)
            else:
                raise Exception('Password mismatch')


def _user_lookup_loader(_, payload):
    username = payload["sub"]

    if username == "anonymous":
        user = User()
        user.username = 'anonymous'
        user.anonymous = True
    else:
        tab = Users()

        sql = f'SELECT username, key, salt, meta FROM {tab.name} WHERE username = ?'
        results = tab.execute(sql, (username,))
        if results:
            _username, key, salt, meta = results[0]
            if _username is None:
                print("User not found")
                user = User()
            else:
                user = User(username, key, salt, meta)
        else:
            print("User not found")
            user = User()

    return user


flask.jwt.user_lookup_loader(_user_lookup_loader)
