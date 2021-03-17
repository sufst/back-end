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
import xml.etree.ElementTree


class Database:
    def __init__(self):
        """
        Create an instance of the back-end server database management module.

        The database management module handles the underlying database used by the back-end (currently just a local
        dictionary). The module provides an helper API to the server to access all required data without having
        to worrying about the underlying database system.

        Future work is to upgrade the local dictionary to a MySQL database.

        The configuration of the database is done through the config.xml configuration file.
        """
        self._db = {}

        self._logger = common.get_logger(type(self).__name__, self._config["verbose"])

        self._logger.info(f"Configuration: {self._config}")

        self._db["users"] = {}

    def _parse_configuration(self):
        self._config = {}
        config_root = xml.etree.ElementTree.parse("config.xml").getroot()

        for field in config_root.iter("database"):
            for config in field.findall("config"):
                self._config[config.attrib["name"]] = config.text

        assert ("verbose" in self._config)

    def put_user(self, user: str, entry: dict) -> None:
        """
        Insert an entry into a user (creates the user if the user is new) in the database.

        :param user: Name of the user.
        :param entry: Dictionary entry to set the user to.
        """
        if user not in self._db["users"]:
            self._db["users"][user] = {}

        self._logger.debug(f"{user} <- {entry}")

        self._db["user"][user] = entry

    def update_user_entry(self, user: str, key: str, value) -> None:
        """
        Update a specific key in a user entry in the database.

        :param user: Name of the user.
        :param key: The key in the user dictionary to update.
        :param value: The value to update the key value to.
        """
        if user in self._db["users"] and key in self._db["users"][user]:
            self._db["users"][user][key] = value

    def get_user(self, user: str) -> dict or None:
        """
        Get the dictionary of a user in the database.

        :param user: Name of the user.
        :return: The dictionary corresponding to the user, or None if user does not exist.
        """
        if user in self._db["users"]:
            return self._db["users"][user]
        else:
            return None
