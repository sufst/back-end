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
import xml.etree.ElementTree
import common.logger


class ConfigurationManager:
    _instance = None
    _config = {}
    _param_mapping = {
        "port": lambda x: int(x),
        "baud": lambda x: int(x),
        "min": lambda x: int(x),
        "max": lambda x: int(x),
        "on_dash": lambda x: x == "True",
        "enable": lambda x: x == "True",
        "id": lambda x: int(x),
        "delay": lambda x: float(x)
    }
    _config_file = "config.xml"
    _logger = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def init_configuration(cls, config_file: str):
        cls._config_file = config_file
        cls._logger = common.logger.get_logger(__name__, "INFO")
        cls._parse_config_file()

    @property
    def configuration(self):
        return self._config

    @classmethod
    def _convert_elem_to_dict(cls, elem):
        components = list(elem)
        entry = {}

        for component in components:
            if len(list(component)) > 0:
                entry[component.attrib["name"]] = cls._convert_elem_to_dict(component)
            else:
                if component.attrib["name"] in cls._param_mapping:
                    entry[component.attrib["name"]] = cls._param_mapping[component.attrib["name"]](component.text)
                else:
                    entry[component.attrib["name"]] = component.text

        return entry

    @classmethod
    def _parse_config_file(cls):
        config_root = xml.etree.ElementTree.parse(cls._config_file).getroot()

        elem_list = list(config_root)

        for elem in elem_list:
            cls._config[elem.tag] = cls._convert_elem_to_dict(elem)

        cls._logger.info("\n" + common.logger.prettify(cls._config))


def get_configuration_manager():
    return ConfigurationManager().get()
