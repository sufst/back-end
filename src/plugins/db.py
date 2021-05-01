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
from src.helpers import config
from sqlite3worker import Sqlite3Worker


class Table:
    columns = [
        'id integer PRIMARY KEY'
    ]

    _cur = None

    def __init__(self):
        self.name = type(self).__name__.lower()

        sql = f"""CREATE TABLE IF NOT EXISTS {self.name} (
                {''.join(map(lambda col: col + ', ', self.columns))[:-2]}
                ) """
        self.execute(sql)

    def execute(self, *args, **kwargs):
        return self._cur.execute(*args, **kwargs)

    @classmethod
    def set_cursor(cls, cur):
        cls._cur = cur


class StageTable(Table):
    pass


def load():
    Table.set_cursor(Sqlite3Worker(config.get_config('database')['Location']))
    StageTable.set_cursor(Sqlite3Worker(config.get_config('database')['StageLocation']))
