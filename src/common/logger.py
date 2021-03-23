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
import logging
import pprint
import os

__pp = pprint.PrettyPrinter(indent=4)
__LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR
}


def get_logger(name, level) -> logging.Logger:
    try:
        os.mkdir("temp")
    except Exception as exc:
        print(repr(exc))

    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(__LEVEL_MAP[level])

        fh = logging.FileHandler("temp/backend.log")
        fh.setLevel(__LEVEL_MAP[level])

        ch = logging.StreamHandler()
        ch.setLevel(__LEVEL_MAP[level])

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


def prettify(text):
    return __pp.pformat(text)
