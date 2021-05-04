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
import os
import zipfile


def zip_folder(src, dst):
    f_zip = zipfile.ZipFile(dst, 'x')

    _zip_dir(src, f_zip)

    f_zip.close()


def _zip_dir(path, zip_h):
    # https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python
    for root, dirs, files in os.walk(path):
        for file in files:
            if 'zip' not in file:
                zip_h.write(os.path.join(root, file),
                            os.path.relpath(os.path.join(root, file),
                                            os.path.join(path, '..')))
