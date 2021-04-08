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
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from sessions import sessions


class SessionList(Resource):
    @staticmethod
    @jwt_required()
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument("name",
                            type=str,
                            help="The name of the session",
                            required=True,
                            location="json")
        parser.add_argument("sensors",
                            type=str,
                            help="A list of sensors to capture on",
                            required=True,
                            location="json")

        args = parser.parse_args(strict=True)

        name = args["name"]
        sensors = args["sensors"]

        print(f"Attempting creating new session {name} -> {sensors}")
        try:
            sessions.create_session(name, sensors)
        except Exception as error:
            print(error)
            return args, 409

    @staticmethod
    @jwt_required()
    def get():
        raise NotImplementedError()


class Session(Resource):
    @staticmethod
    @jwt_required()
    def put(name):
        parser = reqparse.RequestParser()
        parser.add_argument("start",
                            type=bool,
                            help="Start the session with the ",
                            required=False)
        parser.add_argument("end",
                            type=bool,
                            help="End the session",
                            required=False)

        args = parser.parse_args(strict=True)

        arg_handlers = {
            "start": lambda x: sessions.start_session(name) if x else None,
            "end": lambda x: sessions.end_session(name) if x else None
        }

        print(f"Attempting {name} <- {args}")

        for arg, value in args.items():
            arg_handlers[arg](value)
