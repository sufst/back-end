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
from tests.helpers.unittests import unittest
from tests.helpers import config, sessions
import os
import importlib
from tests.plugins import db
from src import main
from multiprocessing import Process


def run_all_units():
    runner = unittest.TextTestRunner()

    for f in os.listdir('./tests/units'):
        if f not in '__init__':
            module = importlib.import_module(f'tests.units.{f.split(".")[0]}')
            if hasattr(module, 'suite'):
                print(f'running {module} suite')
                runner.run(module.suite())


def run_unit(unit):
    runner = unittest.TextTestRunner()

    module = importlib.import_module(f'tests.units.{unit}')
    if hasattr(module, 'suite'):
        print(f'running {module} suite')
        runner.run(module.suite())


def run():
    config.set_config('tests/config_test.ini')

    db.clean_db()
    sessions.clean_sessions()

    pro = Process(target=main.run, args=('tests/config_test.ini',))
    pro.start()

    for f in os.listdir('./tests/plugins'):
        if f not in '__init__':
            module = importlib.import_module(f'tests.plugins.{f.split(".")[0]}')
            if hasattr(module, 'load'):
                module.load()

    # run_unit('noaccount')
    run_unit('sessions')
    # run_all_units()

    pro.kill()


if __name__ == '__main__':
    run()
