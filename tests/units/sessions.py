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
from urllib import request, error
from tests.helpers.unittests import BaseAccountSocketIoTest, unittest
from tests.helpers import users, webapi
import zipfile
import io
import threading
import json
import time


class TestSessions(BaseAccountSocketIoTest):

    def setUp(self):
        self.username = 'testDeveloper'
        self.password = 'testDeveloper'

        try:
            users.create_user(self.username, self.password, 'Developer', {})
        except KeyError:
            pass

        super(TestSessions, self).setUp()

    def test_start_session(self):
        req = webapi.build_request(
            'sessions/test',
            'POST',
            data={'sensors': ['rpm', 'water_temp_c'],
                  'meta': {
                      'test': True
                  }},
            content_type='application/json',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_session_data(self):
        now = time.time()

        data = {
            'rpm': [
                {'epoch': now, 'value': 1},
                {'epoch': now, 'value': 2},
                {'epoch': now, 'value': 3},
                {'epoch': now, 'value': 4},
                {'epoch': now, 'value': 5}
            ],
            'water_temp_c': [
                {'epoch': now, 'value': 6},
                {'epoch': now, 'value': 7},
                {'epoch': now, 'value': 8},
                {'epoch': now, 'value': 9},
                {'epoch': now, 'value': 10}
            ],
            'tps_perc': [
                {'epoch': now, 'value': 11},
                {'epoch': now, 'value': 12},
                {'epoch': now, 'value': 13},
                {'epoch': now, 'value': 14},
                {'epoch': now, 'value': 15}
            ],
        }

        event = threading.Event()

        @self._sio.on('data', namespace='/car')
        def on_meta(_data):
            self.assertTrue(json.loads(_data) == data)
            event.set()

        self._is.sio.emit('data', json.dumps(data), namespace='/car')

        event.wait(timeout=10)

        self.assertTrue(event.isSet())

    def test_session_note(self):
        req = webapi.build_request(
            'sessions/test',
            'PUT',
            data={'note': 'This is patrick'},
            content_type='application/json',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_stop_session(self):
        req = webapi.build_request(
            'sessions/test',
            'PATCH',
            data={'status': 'dead'},
            content_type='application/json',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_get_sessions(self):
        req = webapi.build_request(
            'sessions',
            'GET',
            content_type='application/json',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            f: dict = json.loads(response.read())
            self.assertTrue("test" in f.keys())
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_get_session_zip(self):
        req = webapi.build_request(
            'sessions/test',
            'GET',
            content_type='application/zip',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            f = io.BytesIO(response.read())
            z = zipfile.ZipFile(f, 'r')
            names = z.namelist()
            if ('test/meta.json' in names and 'test/notes.csv' in names and
                    'test/data/rpm.csv' in names and 'test/data/water_temp_c.csv' in names):
                pass
            else:
                self.fail('ZIP file incomplete')
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_get_session_json(self):
        req = webapi.build_request(
            'sessions/test',
            'GET',
            content_type='application/json',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            f = json.loads(response.read())
            if ('data' in f and
                    'meta' in f and
                    'notes' in f):
                pass
            else:
                self.fail('ZIP file incomplete')
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass


def suite():
    s = unittest.TestSuite()

    s.addTest(TestSessions('test_start_session'))
    s.addTest(TestSessions('test_session_data'))
    s.addTest(TestSessions('test_session_note'))
    s.addTest(TestSessions('test_stop_session'))
    s.addTest(TestSessions('test_get_sessions'))
    s.addTest(TestSessions('test_get_session_zip'))
    s.addTest(TestSessions('test_get_session_json'))

    return s
