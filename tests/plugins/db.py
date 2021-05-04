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
from src.plugins import db
from tests.helpers import config
import os
import shutil


Table = db.Table
StageTable = db.StageTable
load = db.load


def clean_db():
    f_db = config.get_config('database')['Location']
    f_stage_db = config.get_config('database')['StageLocation']

    f_db_folder = '/'.join(f_db.split('/')[:-1])
    if not f_db_folder == '' and os.path.exists(f_db_folder):
        shutil.rmtree(f_db_folder)

    f_db_stage_folder = '/'.join(f_stage_db.split('/')[:-1])
    if not f_db_stage_folder == '' and os.path.exists(f_db_stage_folder):
        shutil.rmtree(f_db_stage_folder)
