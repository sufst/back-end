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
from rest.resources import Login, User, Session, SessionList
from flask_restful import Api

__all__ = ["rest"]


class Rest:
    api = None

    def init(self, app):
        print("Starting REST")
        self.api = Api(app)
        self.api.add_resource(User, "/user")
        self.api.add_resource(Login, "/login")
        self.api.add_resource(SessionList, "/session")
        self.api.add_resource(Session, "/session/<string:name>")
        print("Started REST")


rest = Rest()
