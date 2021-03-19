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
import common.database
import os
import werkzeug.security


class UserManagement:
    """
    The User management system handles user requests for creating and authenticating users through usernames and
    passwords. A database is required for the storage of the user accounts.

    User account passwords are hashed and salted for storage.
    """
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
            cls._db = common.database.Database().instance()
            cls._user_id = 0

        return cls._instance

    def create_user(self, username: str, meta: dict) -> None:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", meta["password"].encode("utf-8"), salt, 100000)

        user = common.database.User(self._user_id, username, key, salt)
        self._db.insert_user(user)

        self._user_id += 1

    def is_user_password_correct(self, username: str, password: str) -> bool:
        success = False

        user = self._db.select_user_from_user_name(username)

        if user and werkzeug.security.safe_str_cmp(
                hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), user.salt, 100000),
                user.key):
            success = True

        return success
