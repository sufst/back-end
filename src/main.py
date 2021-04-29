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
from plugins import sio
import os
import importlib


if __name__ == '__main__':
    print(f"SUFST Intermediate-Server Copyright (C) 2021 Nathan Rowley-Smith\n" +
          "This program comes with ABSOLUTELY NO WARRANTY;\n" +
          "This is free software, and you are welcome to redistribute it")

    for f in os.listdir('./plugins'):
        if f not in '__init__':
            module = importlib.import_module(f'plugins.{f.split(".")[0]}')
            if hasattr(module, 'load'):
                module.load()

    for f in os.listdir('./plugins'):
        if f not in '__init__':
            module = importlib.import_module(f'plugins.{f.split(".")[0]}')
            if hasattr(module, 'run'):
                module.run()

    sio.run()
