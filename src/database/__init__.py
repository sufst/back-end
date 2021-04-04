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
from bson import ObjectId

__all__ = ["database", "UserEntry"]


class UserEntry:
    def __init__(self):
        self._id = None
        self.username = None
        self.key = None
        self.salt = None
        self.meta = {
            "has_feet": True
        }

    def get_id(self):
        return self._id

    def set_id(self, value):
        self._id = value

    id = property(get_id, set_id)

    def get_entry(self):
        return {
            "username": self.username,
            "key": self.key,
            "salt": self.salt,
            "meta": self.meta
        }

    def set_entry(self, entry):
        self.id = entry["_id"]
        self.username = entry["username"]
        self.key = entry["key"]
        self.salt = entry["salt"]
        self.meta = entry["meta"]

    entry = property(get_entry, set_entry)


class DatabaseManager:
    mongodb = None

    def init_mongodb(self, mongo_db):
        """
        Initialise the database manager with the mongodb instance.
        :param mongo_db: The mongodb instance.
        """
        self.mongodb = mongo_db

    def insert_new_user(self, user):
        """
        Insert a new user into the database.
        :param user: The new user to insert.
        :return: The unique ID of the new user.
        """
        try:
            self.find_one_user("username", user.username)
        except KeyError:
            return self.mongodb.db.user_accounts.insert_one(user.entry)
        else:
            raise KeyError()

    def find_one_user(self, key, value):
        """
        Find one user based on the key value pair e.g. username bob
        :param key: The key to find with.
        :param value: The value to match against the key.
        :return: The found user (or None)
        """
        if key == "id":
            key = "_id"
            value = ObjectId(value)

        entry = self.mongodb.db.user_accounts.find_one({key: value})
        if entry is not None:
            entry["_id"] = str(entry["_id"])
            user = UserEntry()
            user.entry = entry
            return user
        else:
            raise KeyError()


database = DatabaseManager()
