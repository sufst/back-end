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
import database
import user_management


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
        self._db = database.Database()
        self._usr_mgmt = user_management.UserManagement()

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

        request_handlers = {
            "GET": lambda req: self._restful_serve_get_request(req),
            "POST": lambda req: self._restful_serve_post_request(req)
        }

        if request.get_type() in request_handlers:
            try:
                response, epoch = request_handlers[request.get_type()](request)
            except Exception as exc:
                raise exc
        else:
            raise NotImplementedError

        return response, epoch

    def _restful_serve_post_request(self, request: restful.RestfulRequest):
        dataset_handlers = {
            "users": lambda req, fil: self._restful_serve_post_users_request(req, fil)
        }
        text = request.get_text()

        if request.get_datasets()[0] in dataset_handlers:
            try:
                response, epoch = dataset_handlers[request.get_datasets()[0]](request, text)
            except Exception as exc:
                raise exc
        else:
            raise NotImplementedError

        return response, epoch

    def _restful_serve_post_users_request(self, request: restful.RestfulRequest, text: dict) -> tuple:
        return self._usr_mgmt.create_user(text["username"], text["password"]), time.time()

    def _restful_serve_get_request(self, request: restful.RestfulRequest) -> tuple:
        dataset_handlers = {
            "auth_user": lambda req: self._restful_serve_get_user_auth_request(req)
        }

        if request.get_datasets()[0] in dataset_handlers:
            try:
                response, epoch = dataset_handlers[request.get_datasets()[0]](request)
            except Exception as exc:
                raise exc
        else:
            raise NotImplementedError

        return response, epoch

    def _restful_serve_get_user_auth_request(self, request: restful.RestfulRequest) -> tuple:
        filters = request.get_filters()
        username = filters["username"]
        password = filters["password"]
        return self._usr_mgmt.is_auth_user(username, password), time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.error(f"{exc_type}\n{exc_val}\n{exc_tb}")

