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
import flask_pymongo
import common.user
import bson


class Database:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def init_db(cls, mongo_db: flask_pymongo.PyMongo):
        cls._mongo = mongo_db

    def create_user(self, user: common.user.User) -> None:
        self._mongo.db.user_accounts.insert_one(user.get_record())

    def get_user_from_username(self, username: str) -> common.user.User or None:
        user = common.user.User().from_record(self._mongo.db.user_accounts.find_one({"username": username}))

        return user

    def get_user_from_user_id(self, user_id: str) -> common.user.User or None:
        record = self._mongo.db.user_accounts.find_one({"_id": bson.objectid.ObjectId(user_id)})
        if record:
            user = common.user.User().from_record(record)
        else:
            user = None

        return user

