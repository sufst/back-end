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
from tests.helpers.unittests import BaseAccountTests, unittest
from tests.helpers import users, webapi
import zipfile
import io


class TestDeveloperAccount(BaseAccountTests):

    def setUp(self):
        self.username = 'testDeveloper'
        self.password = 'testDeveloper'

        try:
            users.create_user(self.username, self.password, 'Developer', {})
        except KeyError:
            pass

        super(TestDeveloperAccount, self).setUp()

    def test_create_user(self):
        req = webapi.build_request(
            'user',
            'POST',
            data={'username': 'developer',
                  'password': 'password',
                  'privilege': 'Basic',
                  'meta': {
                      'dept': 'Electronics',
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

    def test_get_session(self):

        req = webapi.build_request(
            'sessions/test',
            'GET',
            token=self.token
        )

        try:
            response = request.urlopen(req)
            f = io.BytesIO(response.read())
            z = zipfile.ZipFile(f, 'r')
            if 'rpm.csv' in z.namelist() and 'water_temp_c.csv' in z.namelist():
                pass
            else:
                self.fail('ZIP file incomplete')
        except error.HTTPError as err:
            self.fail(repr(err))
        else:
            pass


def suite():
    s = unittest.TestSuite()

    s.addTest(TestDeveloperAccount('test_create_user'))
    s.addTest(TestDeveloperAccount('test_get_user'))
    s.addTest(TestDeveloperAccount('test_start_session'))
    s.addTest(TestDeveloperAccount('test_stop_session'))
    s.addTest(TestDeveloperAccount('test_get_session'))

    return s
