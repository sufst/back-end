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
from pymongo import MongoClient
from configuration import config
from time import time

__all__ = ["database", "Document"]


class Document:
    def __init__(self, doc):
        # The _id field from the database is a bson objectID so it needs to be converted to a string for usage.
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        self.__dict__ = doc

    def update(self, other):
        self.__dict__.update(other.__dict__)

    def __str__(self):
        return str(self.__dict__)


class DatabaseManager:
    users = None

    sensors = None
    sessions = None

    def start(self):
        print("Starting database")
        client = MongoClient(config.database["url"])
        self.users = client.users
        self.sensors = client.sensors
        self.sessions = client.sessions
        print("Started database")

    def insert_new_user(self, user):
        """
        Insert a new user into the database.
        :param user: The new user to insert (Made up of a login Document and a meta Document)
        """
        if not self.users.login.find_one("username", user.login.username):
            self.users.login.insert_one(user.login.__dict__)
            self.users.meta.insert_one(user.meta.__dict__)
        else:
            raise KeyError()

    def find_one_user_login(self, key, value):
        """
        Find one user based on the key value pair e.g. username bob
        :param key: The key to find with.
        :param value: The value to match against the key.
        :return: The found user (or None)
        """
        if key == "id":
            key = "_id"
            value = ObjectId(value)

        doc = self.users.login.find_one({key: value})
        if doc is not None:
            user = Document(doc)
            return user
        else:
            raise KeyError()

    def insert_new_sensor_meta(self, name, meta):
        """
        Insert a new document to the emulation sensor's meta collection.

        """
        meta.update(Document({"sensor": name, "epoch": time()}))
        self.sensors["meta"].insert_one(meta.__dict__)

    def insert_new_sensor_data(self, name, data):
        """
        Insert new documents to the sensor's collection.

        """
        insert = []
        for entry in data:
            insert.append(entry.__dict__)

        self.sensors[name].insert_many(insert)


database = DatabaseManager()
