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
from tests.helpers.unittests import BaseAccountTests, unittest, BaseAccountSocketIoTest
from tests.helpers import users, webapi
import zipfile
import io
import threading
import json


class TestDeveloperAccount(BaseAccountTests):

    def setUp(self):
        self.username = 'testDeveloper'
        self.password = 'testDeveloper'

        try:
            users.create_user(self.username, self.password, 'Developer', 'Tier 1', {})
        except KeyError:
            pass

        super(TestDeveloperAccount, self).setUp()

    def test_create_user(self):
        req = webapi.build_request(
            'users/developer',
            'POST',
            data={'password': 'password',
                  'privilege': 'Basic',
                  'department': 'Tier 1',
                  'meta': {
                      'memberType': 'Member'
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

    def test_get_user(self):
        req = webapi.build_request(
            'user',
            'GET',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_change_dummy_department(self):
        req = webapi.build_request(
            'users/developer',
            'PATCH',
            token=self.token,
            data={'department': 'Electronics'},
            content_type='application/json'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.fail(f'{err.reason}: {err.read()}')
        else:
            pass

    def test_get_dummy_changed_department(self):
        req = webapi.build_request(
            'users/developer',
            'GET',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            meta = json.loads(response.read())
            self.assertTrue('privilege' in meta)
            self.assertTrue('department' in meta)
            self.assertTrue(meta['privilege'] == 'Basic')
            self.assertTrue(meta['department'] == 'Electronics')
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_change_department(self):
        req = webapi.build_request(
            'user',
            'PATCH',
            token=self.token,
            data={'department': 'Electronics'},
            content_type='application/json',
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.fail(err.reason)
        else:
            pass

    def test_get_changed_department(self):
        req = webapi.build_request(
            'user',
            'GET',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            meta = json.loads(response.read())
            self.assertTrue('privilege' in meta)
            self.assertTrue('department' in meta)
            self.assertTrue(meta['privilege'] == 'Developer')
            self.assertTrue(meta['department'] == 'Electronics')
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_change_wrong_department(self):
        req = webapi.build_request(
            'user',
            'PATCH',
            token=self.token,
            data={'department': 'WRONG'},
            content_type='application/json',
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 400)
        else:
            self.fail('Back-End accepted switching to wrong department ')

    def test_get_all_users(self):
        req = webapi.build_request(
            'users',
            'GET',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            data = json.loads(response.read())
            self.assertTrue('users' in data)
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_get_didnot_change_department(self):
        req = webapi.build_request(
            'user',
            'GET',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            meta = json.loads(response.read())
            self.assertTrue('privilege' in meta)
            self.assertTrue('department' in meta)
            self.assertTrue(meta['privilege'] == 'Developer')
            self.assertTrue(meta['department'] == 'Electronics')
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_start_session(self):
        req = webapi.build_request(
            'sessions/developer',
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

    def test_stop_session(self):
        req = webapi.build_request(
            'sessions/developer',
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

    def test_get_session_zip(self):
        req = webapi.build_request(
            'sessions/developer',
            'GET',
            content_type='application/zip',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            f = io.BytesIO(response.read())
            z = zipfile.ZipFile(f, 'r')
            names = z.namelist()
            if ('developer/meta.json' in names and 'developer/notes.csv' in names and
                    'developer/data/rpm.csv' in names and 'developer/data/water_temp_c.csv' in names):
                pass
            else:
                self.fail('ZIP file incomplete')
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass

    def test_get_session_json(self):
        req = webapi.build_request(
            'sessions/developer',
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


class TestDeveloperAccountSocketIO(BaseAccountSocketIoTest):
    def setUp(self):
        self.username = 'testDeveloper'
        self.password = 'testDeveloper'

        super(TestDeveloperAccountSocketIO, self).setUp()

    def test_socket_io_connect(self):
        pass

    def test_socket_io_meta(self):
        meta = {
            "rpm": {
                "name": "RPM",
                "units": "RPM",
                "enable": True,
                "group": "Core",
                "min": 0,
                "max": 10000,
                "on_dash": True,
                "emulation": "int(5000 * modules.math.sin(modules.math.radians(x * 10)) + 5000)"
            },
            "water_temp_c": {
                "name": "Water Temp",
                "units": "C",
                "enable": True,
                "group": "Core",
                "min": 0,
                "max": 120,
                "on_dash": True,
                "emulation": "modules.random.randint(80, 100)"
            }
        }

        event = threading.Event()

        @self._sio.on('meta', namespace='/car')
        def on_meta(_meta):
            self.assertTrue(json.loads(_meta) == meta)
            event.set()

        self._is.sio.emit('meta', json.dumps(meta), namespace='/car')

        event.wait(timeout=10)

        self.assertTrue(event.isSet())

    def test_socket_io_data(self):
        data = {
            "rpm": [1, 2, 3, 4, 5, 6],
            "water_temp_c": [1, 2, 3, 4, 5, 6]
        }

        event = threading.Event()

        @self._sio.on('data', namespace='/car')
        def on_meta(_data):
            self.assertTrue(json.loads(_data) == data)
            event.set()

        self._is.sio.emit('data', json.dumps(data), namespace='/car')

        event.wait(timeout=10)

        self.assertTrue(event.isSet())


def suite():
    s = unittest.TestSuite()

    s.addTest(TestDeveloperAccount('test_create_user'))
    s.addTest(TestDeveloperAccount('test_get_user'))

    s.addTest(TestDeveloperAccount('test_change_dummy_department'))
    s.addTest(TestDeveloperAccount('test_get_dummy_changed_department'))
    s.addTest(TestDeveloperAccount('test_change_department'))
    s.addTest(TestDeveloperAccount('test_get_changed_department'))
    s.addTest(TestDeveloperAccount('test_change_wrong_department'))
    s.addTest(TestDeveloperAccount('test_get_didnot_change_department'))

    s.addTest(TestDeveloperAccount('test_get_all_users'))

    s.addTest(TestDeveloperAccount('test_start_session'))
    s.addTest(TestDeveloperAccount('test_stop_session'))
    s.addTest(TestDeveloperAccount('test_get_session_json'))
    s.addTest(TestDeveloperAccount('test_get_session_zip'))

    s.addTest(TestDeveloperAccountSocketIO('test_socket_io_connect'))
    s.addTest(TestDeveloperAccountSocketIO('test_socket_io_meta'))
    s.addTest(TestDeveloperAccountSocketIO('test_socket_io_data'))

    return s
