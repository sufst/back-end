"""
    Southampton University Formula Student Team Intermediate Server
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

import common
import hashlib
import xml.etree.ElementTree
import database
import os


class UserManagement:
    def __init__(self):
        """
        Create an instance of the user management system.

        The User management system handles user requests for creating and authenticating users through usernames and
        passwords. A database is required for the storage of the user accounts.

        User account passwords are hashed and salted for storage.
        """
        self._parse_configuration()

        self._logger = common.get_logger(type(self).__name__, self._config["verbose"])

        self._logger.info(f"Configuration: {self._config}")

        self._db = database.Database()

    def _parse_configuration(self):
        self._config = {}
        config_root = xml.etree.ElementTree.parse("config.xml").getroot()

        for field in config_root.iter("server"):
            for config in field.findall("config"):
                self._config[config.attrib["name"]] = config.text

        assert ("verbose" in self._config)

    def create_user(self, username: str, password: str) -> bool:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)

        user = {"key": key, "salt": salt}
        return self._db.put_user(username, user)

    def is_auth_user(self, username: str, password: str) -> bool:
        success = False
        user = self._db.get_user(username)

        if user is not None:
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), user["salt"], 100000)
            if key == user["key"]:
                success = True

        return success

