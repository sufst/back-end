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
import asyncio
import json
import websockets
import ssl

import common
import xml.etree.ElementTree


class RestfulRequest:
    def __init__(self, request_str: str):
        """
        Sub class for encapsulating a RESTful request and response.
        :param request_str: The RESTful request string received.
        """
        self._request_str = request_str

        self._dataset, self._filters, self._type = None, {}, None

        self._decode_request()

    def _decode_request(self) -> None:
        """
        Decode the RESTful request string to determine the type, dataset, and filters wanted.
        """

        type_decoders = {
            "GET": lambda x: self._decode_get_request(x),
            "PUT": lambda x: self._decode_put_request(x),
            "POST": lambda x: self._decode_post_request(x)
        }

        split_space = self._request_str.split(" ")
        self._type = split_space[0]

        if self._type in type_decoders:
            type_decoders[self._type](split_space)
        else:
            raise NotImplementedError

    def _decode_post_request(self, split_space: str):
        # Decode POST /users {"username": "username", "password": "password"}
        self._dataset = split_space[1]
        self._datasets = self._dataset.split("/")[1:]
        self._text = json.loads(split_space[2])

    def _decode_put_request(self, split_space: str):
        raise NotImplementedError

    def _decode_get_request(self, split_space: str):
        # Decode GET /sensors/RPM?timesince=<epoch>&amount=<n>

        split_question = split_space[1].split("?")
        self._dataset = split_question[0]
        self._datasets = self._dataset.split("/")[1:]
        split_and = split_question[1].split("&")

        if not split_and[0] == '':
            for fil_value in split_and:
                entry = fil_value.split("=")
                self._filters[entry[0]] = entry[1]

    def get_type(self) -> str:
        """
        Get the type of the request.
        """
        return self._type

    def get_dataset(self) -> str:
        """
        Get the dataset (in a single string combined).
        """
        return self._dataset

    def get_datasets(self) -> list:
        """
        Get the datasets (in a list form )
        """
        return self._datasets

    def get_filters(self) -> dict:
        """
        Get the filters.
        """
        return self._filters

    def get_text(self) -> dict:
        """
        Get the text (dictionary) of a POST request.
        """
        return self._text

    def __str__(self) -> str:
        return str({"type": self._type, "dataset": self._dataset, "filters": self._filters})


class Restful:
    def __init__(self):
        """
        Initialise the RESTful server to handle RESTful requests over the websocket.

        The RESTful server will invoke the callable passed in def server with the request in the form
        of the RestfulRequest sub class. The RestfulRequest sub class provides the type, datasets, and filters
        the RESTful requests is made up with. A response can be sent back to the client by returning a Dict
        in the callable function.
        """
        self._parse_configuration()

        self._logger = common.get_logger("Restful", self._config["verbose"])

        self._logger.info(f"Configuration: {self._config}")

        if self._config["secure"]:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self._config["cert"], self._config["key"])
            self._server = websockets.serve(self._websocket_serve, self._config["url"], self._config["port"],
                                            ssl=ssl_context)
        else:
            self._server = websockets.serve(self._websocket_serve, self._config["url"], self._config["port"])

        self._request_callable = None

    def _parse_configuration(self):
        config_root = xml.etree.ElementTree.parse("config.xml").getroot()
        self._config = {}

        type_mapping = {
            "secure": lambda x: x == "True",
            "port": lambda x: int(x),
            "keep_alive": lambda x: x == "True"
        }

        for field in config_root.iter("RESTful"):
            for config in field.findall("config"):
                if config.attrib["name"] in type_mapping:
                    self._config[config.attrib["name"]] = type_mapping[config.attrib["name"]](config.text)
                else:
                    self._config[config.attrib["name"]] = config.text

        assert("url" in self._config)
        assert("port" in self._config)
        assert("verbose" in self._config)
        assert("keep_alive" in self._config)
        assert("secure" in self._config)
        if self._config["secure"]:
            assert("cert" in self._config)
            assert("key" in self._config)

    def serve(self, request_callable):
        """
        Start the server to serve network requests.
        :param request_callable: Callback function for serving received requests.
        """
        self._request_callable = request_callable

        asyncio.get_event_loop().run_until_complete(self._server)
        if self._config["secure"]:
            self._logger.info(f"Serving on wss://{self._config['url']}:{self._config['port']}")
        else:
            self._logger.info(f"Serving on ws://{self._config['url']}:{self._config['port']}")

    async def _websocket_serve(self, websocket, path: str):
        """
        Serve a new websocket client.
        :param websocket: The new websocket object.
        :param path: The accessed path from the client.
        """
        try:
            while self._config["keep_alive"]:
                request = await websocket.recv()
                self._logger.info(f"Got request: {request}")

                response = {"status": 200, "result": {}, "epoch": 0}

                try:
                    request = RestfulRequest(request)
                except Exception as error:
                    self._logger.error(error)
                    response["status"] = 400
                else:
                    try:
                        response["result"], response["epoch"] = self._request_callable(request)
                    except NotImplementedError:
                        response["status"] = 501
                    except SystemError:
                        response["status"] = 500
                    except FileNotFoundError:
                        response["status"] = 404

                self._logger.info(f"Response <- {response}")
                await websocket.send(json.dumps(response))

            websocket.close()
        except websockets.ConnectionClosedOK:
            pass
        except websockets.ConnectionClosedError:
            pass
