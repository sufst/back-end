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
import hashlib
from database import database
from database import UserEntry
import os
import werkzeug.security
import functools
import flask_socketio
import flask_jwt_extended

__all__ = ["usersManager", "User"]


class User(flask_login.UserMixin):
    def __init__(self):
        self.id = None
        self.username = None
        self.authenticated = False
        self.active = False
        self.anonymous = False
        self.access_token = None

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_anonymous(self):
        return self.anonymous


class UserManager:
    """
    The User management system handles user requests for creating and authenticating users through usernames and
    passwords. A database is required for the storage of the user accounts.

    User account passwords are hashed and salted for storage.
    """
    user_tokens = {}

    @staticmethod
    def create_user(username, password):
        try:
            database.find_one_user("username", username)
        except KeyError:
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)

            user_entry = UserEntry()

            user_entry.username = username
            user_entry.key = key
            user_entry.salt = salt

            database.insert_new_user(user_entry)
        else:
            raise KeyError()

    def login_user(self, username, password):
        try:
            user_entry = database.find_one_user("username", username)
        except KeyError as error:
            raise error
        else:
            if werkzeug.security.safe_str_cmp(
                    hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), user_entry.salt, 100000),
                    user_entry.key):

                user = User()
                user.id = user_entry.id
                user.username = user_entry.username

                token = flask_jwt_extended.create_access_token(identity=user.id)
                self.user_tokens[token] = user

                user.authenticated = True
                user.active = True
                if flask_login.login_user(user):
                    print(f"{user.username} logged in")

                return token
            else:
                raise KeyError()

    @staticmethod
    def get_user_meta(username):
        try:
            user_entry = database.find_one_user("username", username)
        except KeyError as error:
            raise error
        else:
            return user_entry.meta

    def request_loader(self, request):
        access_token = request.args.get("access_token")

        try:
            return self.user_tokens[access_token]
        except KeyError:
            return None

    @staticmethod
    def authenticated_only(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                flask_socketio.disconnect()
            else:
                return func(*args, **kwargs)

        return wrapped


usersManager = UserManager()
