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
from database import database, Document
import os
import werkzeug.security
import flask_jwt_extended
import flask

__all__ = ["usersManager", "User"]


class User(flask_login.UserMixin):
    def __init__(self, login=None, meta=None):
        self.login = login or None
        self.meta = meta or None

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


class UserManager:
    """
    The User management system handles user requests for creating and authenticating users through usernames and
    passwords. A database is required for the storage of the user accounts.

    User account passwords are hashed and salted for storage.
    """
    user_tokens = {}

    @staticmethod
    def create_user(username, password, meta):
        print(f"Attempting user create -> {username}")
        try:
            database.find_one_user_login("username", username)
        except KeyError:
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)

            login_doc = Document({"username": username, "key": key, "salt": salt})
            meta_doc = Document(meta)

            user = Document({"login": login_doc, "meta": meta_doc})

            database.insert_new_user(user)
            print(f"User created {user}")
        else:
            print("User already exists")
            raise KeyError()

    @staticmethod
    def auth_user(username, password):
        print(f"Attempting auth user -> {username}")
        try:
            user = User(login=database.find_one_user_login("username", username))
        except KeyError as error:
            print("User does not exist")
            raise error
        else:
            if werkzeug.security.safe_str_cmp(
                    hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), user.login.salt, 100000),
                    user.login.key):

                token = flask_jwt_extended.create_access_token(identity=user.login.id, expires_delta=False)

                print("Token issued")
                return token
            else:
                print("Password mismatch")
                raise KeyError()

    @staticmethod
    def user_lookup_loader(_, payload):
        user_id = payload["sub"]
        try:
            return User(login=database.find_one_user_login("id", payload["sub"]))
        except KeyError:
            print("User not found")
            return None


usersManager = UserManager()
