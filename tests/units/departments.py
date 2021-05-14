"""
    Southampton University Formula Student Team Back-End
    Copyright (C) 2021 SUFST

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


class TestElectronicsDepartment(BaseAccountTests):
   
   def setUp(self):
        self.username = 'testElec'
        self.password = 'testElec'

        try:
            users.create_user(self.username, self.password, 'Developer', 'Electronics', {})
        except KeyError:
            pass

        super(TestElectronicsDepartment, self).setUp()

   def test_create_user(self):
        req = webapi.build_request(
            'users/developer',
            'POST',
            data={'password': 'password',
                  'privilege': 'Basic',
                  'department': 'Electronics'
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
            

def suite():
    s = unittest.TestSuite()

    s.addTest(TestElectronicsDepartment('test_create_user'))
    s.addTest(TestElectronicsDepartment('test_get_user'))
    
    return s
