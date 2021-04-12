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
from flask_jwt_extended import jwt_required, current_user
from sessions import sessions, Session as SensorsSession
from flask import jsonify


class SessionList(Resource):
    @staticmethod
    @jwt_required()
    def post():
        if not current_user.is_anonymous:
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

            print(f"Attempting session {name} POST {sensors}")
            try:
                sessions.create(SensorsSession(name, sensors))
            except Exception as error:
                print(error)
                return args, 409
        else:
            return None, 401

    @staticmethod
    @jwt_required()
    def get():
        print(f"Attempting sessions GET")
        return jsonify(sessions.list())


class Session(Resource):
    @staticmethod
    @jwt_required()
    def put(name):
        if not current_user.is_anonymous:
            parser = reqparse.RequestParser()
            parser.add_argument("start",
                                type=bool,
                                help="Start the session",
                                required=False)
            parser.add_argument("end",
                                type=bool,
                                help="End the session",
                                required=False)
            parser.add_argument("note",
                                type=str,
                                help="A note to save to the session",
                                required=False)

            args = parser.parse_args(strict=True)

            try:
                sess = sessions.get(name)
            except Exception as error:
                print(error)
                return name, 409

            arg_handlers = {
                "start": lambda x: sess.start() if x else None,
                "end": lambda x: sess.end() if x else None
            }

            print(f"Attempting session {name} PUT {args}")

            for arg, value in args.items():
                if value is not None:
                    arg_handlers[arg](value)
        else:
            return None, 401

    @staticmethod
    def get(name):
        print(f"Attempting session {name} GET")
        try:
            return sessions.get(name).get()
        except KeyError as error:
            print(error)
            return name, 409
