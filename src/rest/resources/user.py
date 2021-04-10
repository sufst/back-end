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
from users import users
from flask_jwt_extended import current_user, jwt_required


class User(Resource):
    @staticmethod
    @jwt_required()
    def get():
        return current_user.meta

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument("username",
                            type=str,
                            help="Username to login with",
                            required=True,
                            location="json")
        parser.add_argument("password",
                            type=str,
                            help="Password to login with",
                            required=True,
                            location="json")
        parser.add_argument("likes_beans",
                            type=bool,
                            help="Whether the user likes beans or not",
                            required=False,
                            location="json")

        args = parser.parse_args(strict=True)

        meta = {
            "likes_beans": args["likes_beans"] or None
        }

        try:
            print(f"Attempting user create -> {args['username']} -> {meta}")
            users.create_user(args["username"], args["password"], meta)
        except KeyError as error:
            print(error)
            return str(error), 409
