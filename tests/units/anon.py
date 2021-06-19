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
from tests.helpers import webapi, users
import threading
import json


class TestAnonAccount(BaseAccountTests):
    def setUp(self):
        self.username = 'anonymous'
        self.password = 'anonymous'

        try:
            users.create_user('dummyAnon', 'dummyAnon', 'Basic', 'Electronics', {})
        except KeyError:
            pass

        super(TestAnonAccount, self).setUp()

    def test_create_user(self):
        req = webapi.build_request(
            'users/username',
            'POST',
            data={'password': 'password',
                  'privilege': 'Basic',
                  'department': 'Electronics',
                  'meta': {
                      'memberType': 'Member'
                  }},
            content_type='application/json'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            self.fail()

    def test_get_user(self):
        req = webapi.build_request(
            'user',
            'GET'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            self.fail()

    def test_get_dummy_user(self):
        req = webapi.build_request(
            'users/dummyAnon',
            'GET',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            pass

    def test_raise_dummy_privilege(self):
        req = webapi.build_request(
            'users/dummyAnon',
            'PATCH',
            data={'privilege': 'Admin'},
            content_type='application/json',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            pass

    def test_get_dummy_admin_raised(self):
        req = webapi.build_request(
            'users/dummyAnon',
            'GET',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
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
            self.assertTrue(err.code == 401)
        else:
            self.fail('Anon User changed department')

    def test_get_changed_department(self):
        req = webapi.build_request(
            'user',
            'GET',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            self.fail('Anon User should not access GET')

    def test_get_all_users(self):
        req = webapi.build_request(
            'users',
            'GET',
            token=self.token,
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            self.fail('Anonymous User Got all Users')

    def test_start_session(self):
        req = webapi.build_request(
            'sessions/anon',
            'POST',
            data={'sensors': ['rpm', 'water_temp_c'],
                  'meta': {
                      'test': True
                  }},
            content_type='application/json'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            pass

    def test_stop_session(self):
        req = webapi.build_request(
            'sessions/anon',
            'PATCH',
            data={'status': 'dead'},
            content_type='application/json'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            pass

    def test_get_session_zip(self):
        req = webapi.build_request(
            'sessions/anon',
            'GET',
            content_type='application/zip',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code != 401)
        else:
            pass

    def test_get_session_json(self):
        req = webapi.build_request(
            'sessions/anon',
            'GET',
            content_type='application/json',
            token=self.token
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code != 401)
        else:
            pass


class TestAnonAccountSocketIO(BaseAccountSocketIoTest):
    def setUp(self):
        self.username = 'anonymous'
        self.password = 'anonymous'

        super(TestAnonAccountSocketIO, self).setUp()

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

    s.addTest(TestAnonAccount('test_create_user'))
    s.addTest(TestAnonAccount('test_get_user'))
    s.addTest(TestAnonAccount('test_get_dummy_user'))
    s.addTest(TestAnonAccount('test_raise_dummy_privilege'))
    s.addTest(TestAnonAccount('test_get_dummy_admin_raised'))

    s.addTest(TestAnonAccount('test_change_department'))
    s.addTest(TestAnonAccount('test_get_changed_department'))

    s.addTest(TestAnonAccount('test_get_all_users'))

    s.addTest(TestAnonAccount('test_start_session'))
    s.addTest(TestAnonAccount('test_stop_session'))
    s.addTest(TestAnonAccount('test_get_session_json'))
    s.addTest(TestAnonAccount('test_get_session_zip'))

    s.addTest(TestAnonAccountSocketIO('test_socket_io_connect'))
    s.addTest(TestAnonAccountSocketIO('test_socket_io_meta'))
    s.addTest(TestAnonAccountSocketIO('test_socket_io_data'))

    return s
