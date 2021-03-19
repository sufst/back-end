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


class User:
    def __init__(self, user_id, username, key, salt):
        self.id = user_id
        self.username = username
        self.key = key
        self.salt = salt

    def __str__(self):
        return f"User {self.id}"


class Database:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
            cls._mysql = {"users": {}, "username_to_id": {}}
        return cls._instance

    def insert_user(self, user: User) -> None:
        self._mysql["users"][user.id] = user
        self._mysql["username_to_id"][user.username] = user.id

    def select_user_from_user_id(self, user_id: int) -> User or None:
        if user_id in self._mysql:
            return self._mysql["users"][user_id]
        else:
            return None

    def select_user_from_user_name(self, username: str) -> User or None:
        if username in self._mysql["username_to_id"]:
            return self._mysql["users"][self._mysql["username_to_id"][username]]
        else:
            return None

