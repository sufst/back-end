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
import xml.etree.ElementTree

__all__ = ["config"]


class ConfigurationManager:
    master_config = {}

    def init_config(self):
        self._init_config_database()

    def _build_dict_from_elem(self, elem, type_conversions):
        parsed = {}

        for entry in iter(elem):
            tag = entry.tag
            if len(entry) > 0:
                parsed[tag] = self._build_dict_from_elem(entry, type_conversions)
            else:
                text = entry.text
                if tag in type_conversions:
                    parsed[tag] = type_conversions[tag](text)
                else:
                    parsed[tag] = text
        return parsed

    def _init_config_database(self):
        root = xml.etree.ElementTree.parse("database.xml").getroot()

        parsed = self._build_dict_from_elem(root, {})

        self.master_config["database"] = parsed

    @property
    def database(self):
        return self.master_config["database"]


config = ConfigurationManager()
