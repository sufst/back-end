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
from tests.helpers.unittests import BaseTest, unittest
from tests.helpers import webapi


class TestNoAccount(BaseTest):
    def test_create_user(self):
        req = webapi.build_request(
            'users/username',
            'POST',
            data={'password': 'password',
                  'privilege': 'Basic',
                  'meta': {
                      'dept': 'Electronics',
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

    def test_get_all_users(self):
        req = webapi.build_request(
            'users',
            'GET',
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code == 401)
        else:
            self.fail('No Account User Got all Users')

    def test_get_session(self):
        req = webapi.build_request(
            'sessions/test',
            'GET'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code != 401)
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
            'sessions/test',
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
            'sessions/test',
            'GET',
            content_type='application/zip'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code != 401)
        else:
            pass

    def test_get_session_json(self):
        req = webapi.build_request(
            'sessions/test',
            'GET',
            content_type='application/json'
        )

        try:
            request.urlopen(req)
        except error.HTTPError as err:
            self.assertTrue(err.code != 401)
        else:
            pass


def suite():
    s = unittest.TestSuite()

    s.addTest(TestNoAccount('test_create_user'))
    s.addTest(TestNoAccount('test_get_user'))
    s.addTest(TestNoAccount('test_get_all_users'))

    s.addTest(TestNoAccount('test_start_session'))
    s.addTest(TestNoAccount('test_stop_session'))
    s.addTest(TestNoAccount('test_get_session_json'))
    s.addTest(TestNoAccount('test_get_session_zip'))

    return s
