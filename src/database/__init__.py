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

    def start(self) -> None:
        print("Starting database")
        client = MongoClient(config.database["url"])
        self.users = client.users
        self.sensors = client.sensors
        self.sessions = client.sessions
        print("Started database")

    def find_one(self, collection, query):
        entry = collection.find_one(query)
        if entry is not None:
            return self._get_document_from_entry(entry)
        else:
            return None

    @staticmethod
    def _get_entries_from_documents(documents):
        return list(map(lambda x: x.__dict__, documents))

    @staticmethod
    def _get_entry_from_document(document):
        return document.__dict__

    @staticmethod
    def _get_document_from_entry(entry):
        return Document(entry)

    @staticmethod
    def _get_documents_from_entries(entries):
        return list(map(lambda x: Document(x), entries))

    def insert_new_user(self, user):
        """
        Insert a new user into the database.
        :rtype: Returns the user ID
        :param user: The new user to insert (Made up of a login Document and a meta Document)
        """
        if not self.users.login.find_one("username", user.login.username):
            user_id = self.users.login.insert_one(self._get_entry_from_document(user.login))
            self.users.meta.insert_one(self._get_entry_from_document(user.meta))

            return user_id
        else:
            raise KeyError(f"{user.login.username} already exists")

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

        return self.find_one(self.users.login, {key: value})

    def insert_sensor_collection(self, sensor):
        """
        Attempts to insert a sensor collection into the sensor database.
        If the collection already exists then nothing happens.

        :param sensor: The sensor document which contains .name and a .initial document to create the new collection
                        with.
        """
        if sensor.name not in self.sensors.list_collection_names():
            collection = self.sensors[sensor.name]
            collection.insert_one(self._get_entry_from_document(sensor.initial))

    def insert_to_sensor_many(self, sensor, docs):
        """
        Inserts sensor documents into the sensor collection.

        :param sensor: The sensor name.
        :param docs: The list of documents to insert.
        :return The list of inserted IDs.
        """
        collection = self.sensors[sensor]
        return list(map(lambda x: str(x), collection.insert_many(
            self._get_entries_from_documents(docs)).inserted_ids))

    def find_from_sensor_many(self, sensor, query):
        """
        Find all documents in a sensor collection based on the query.
        :param sensor: The sensor name.
        :param query: A query in the form of {<field>: [<value>,...]}
        """
        mongodb_query = {}
        for field in query:
            if query[field] == "id":
                mongodb_query = {"_id", {"$in": list(map(lambda x: ObjectId(x), query[field]))}}
            else:
                mongodb_query = {field: {"$in": query[field]}}

        return self._get_documents_from_entries(self.sensors[sensor].find(mongodb_query))

    def find_sensor_meta(self, name, meta_id):
        """
        Find and return a sensor in the database.
        :param meta_id: The ID of the meta insertion
        :param name: The name of the sensor to find.
        :return: The meta (or None)
        """
        return self.find_one(self.sensors[name], {"_id": ObjectId(meta_id)})

    def find_from_sensor_many_from_ids(self, sensor, many):
        """
        Find all sensor data from a sensor based on the ID of the sensor data documents.

        :param sensor: The name of the sensor.
        :param many: List of IDs.
        """
        many = list(map(lambda x: ObjectId(x), many))
        return self._get_documents_from_entries(self.sensors[sensor].query({"_id": {many}}))

    def insert_session_collection(self, name, doc):
        """
        Insert a new session collection into the sessions database.
        Raises an error if the session name already exists.

        :param name: The sessions name.
        :param doc: The creation document.
        """
        if name in self.sessions.list_collection_names():
            raise IndexError(f"Session {name} already exists")
        else:
            ses = self.sessions[name]
            ses.insert_one(self._get_entry_from_document(doc))

    def insert_to_session_many(self, name, many):
        """
        Insert many documents into a session.

        :param name: The name of the session.
        :param many: The list of documents to insert.
        """
        ses = self.sessions[name]
        ses.insert_many(self._get_entries_from_documents(many))

    def find_session_collection(self, name):
        """
        Find and return a session (returns the session collection).

        :param name: The session name
        :return: The collection (or None)
        """
        return self.sessions[name]


database = DatabaseManager()
