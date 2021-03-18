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
import jwt
import os


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

        self._token_key = os.urandom(16)

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

        handlers = {
            "GET": {

            },
            "POST": {
                "/users": lambda req: self._restful_serve_post_users_request(req),
                "/users/token": lambda req: self._restful_serve_post_users_token_request(req)
            },
            "PUT": {

            },
            "DELETE": {

            }
        }

        req_type = request.get_type()
        if req_type in handlers:
            req_dataset = request.get_dataset()
            if req_dataset in handlers[req_type]:
                try:
                    response, epoch = handlers[req_type][req_dataset](request)
                except Exception as exc:
                    raise exc
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

        return response, epoch

    def _restful_serve_post_users_token_request(self, request: restful.RestfulRequest) -> tuple:
        response = {}

        text = request.get_text()
        username = text["username"]
        password = text["password"]

        if self._usr_mgmt.is_auth_user(username, password):
            response["valid_user"] = True
            response["token"] = jwt.encode(
                {"username": username, "privilege": "user"}, self._token_key, algorithm="HS256")
        else:
            response["valid_user"] = False

        return response, time.time()

    def _restful_serve_post_users_request(self, request: restful.RestfulRequest) -> tuple:
        text = request.get_text()
        return self._usr_mgmt.create_user(text["username"], text["password"]), time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.error(f"{exc_type}\n{exc_val}\n{exc_tb}")

