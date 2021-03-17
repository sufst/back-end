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
import restful
import xml.etree.ElementTree
import asyncio
import time


class Server:
    def __init__(self):
        """
        Create an instance of the back-end server

        The back-end server provides features for the front-end to operate correctly (user account management and
        long-term session data storage), along with a permanent storage for sensor data from the intermediate-server.

        The configuration of the back-end server is done through the config.xml configuration file.
        """
        self._parse_configuration()

        self._logger = common.get_logger(type(self).__name__, self._config["verbose"])

        self._logger.info(f"Configuration: {self._config}")

        self._restful = restful.Restful()

    def _parse_configuration(self):
        self._config = {}
        config_root = xml.etree.ElementTree.parse("config.xml").getroot()

        for field in config_root.iter("server"):
            for config in field.findall("config"):
                self._config[config.attrib["name"]] = config.text

        assert ("verbose" in self._config)

    def serve_forever(self) -> None:
        """
        Serve the server forever.

        This starts the RESTful API.
        """
        self._restful.serve(self._restful_serve)

        try:
            asyncio.get_event_loop().run_forever()
        finally:
            print("End")

    def _restful_serve(self, request: restful.RestfulRequest) -> tuple:
        self._logger.info(f"Serving: {request}")

        request_handlers = {"GET": lambda req, fil: self._restful_server_get_request(req, fil)}

        if request.get_type() in request_handlers:
            try:
                response, epoch = request_handlers[request.get_type()](request, request.get_filters())
            except Exception as exc:
                raise exc
        else:
            raise NotImplementedError

        return response, epoch

    def _restful_server_get_request(self, request: restful.RestfulRequest, filters: dict) -> tuple:
        dataset_handlers = {"auth_user": lambda req, fil: self._restful_serve_get_name_request(req, fil)}

        if request.get_datasets()[0] in dataset_handlers:
            try:
                response, epoch = dataset_handlers[request.get_datasets()[0]](request, filters)
            except Exception as exc:
                raise exc
        else:
            raise NotImplementedError

        return response, epoch

    def _restful_serve_get_name_request(self, request: restful.RestfulRequest, filters: dict) -> tuple:
        print(request)
        print(filters)

        return "user", time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.error(f"{exc_type}\n{exc_val}\n{exc_tb}")

