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
import sqlite3
from helpers import config

_conf = config.config['database']
_con = sqlite3.connect(_conf['Location'])
_cur = _con.cursor()
_s_con = sqlite3.connect(_conf['StageLocation'])
_s_cur = _s_con.cursor()


class Table:
    columns = [
        'id integer PRIMARY KEY'
    ]

    con = _con
    cur = _cur

    def __init__(self):
        self.name = type(self).__name__.lower()
        sql = f"""CREATE TABLE IF NOT EXISTS {self.name} (
                {''.join(map(lambda col: col + ', ', self.columns))[:-2]}
                ) """
        self.cur.execute(sql)

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(exc_val)
        else:
            self.con.commit()


class StageTable(Table):
    con = _s_con
    cur = _s_cur

