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
import os


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
    f_db = config.get_config('database')['Location']
    f_stage_db = config.get_config('database')['StageLocation']

    f_db_folder = '/'.join(f_db.split('/')[:-1])
    if not f_db_folder == '' and not os.path.exists(f_db_folder):
        os.makedirs(f_db_folder)

    f_db_stage_folder = '/'.join(f_stage_db.split('/')[:-1])
    if not f_db_stage_folder == '' and not os.path.exists(f_db_stage_folder):
        os.makedirs(f_db_stage_folder)

    Table.set_cursor(Sqlite3Worker(f_db))
    StageTable.set_cursor(Sqlite3Worker(f_stage_db))
