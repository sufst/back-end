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
import unittest
from src import main
from multiprocessing import Process
from tests.helpers import config, webapi
import json
from urllib import request, error
from socketio import Client


class BaseTest(unittest.TestCase):

    def setUp(self):
        self._pro = Process(target=main.run, args=('tests/config_test.ini',))

        self._pro.start()
        self._conf = config.get_config('server')

    def tearDown(self):
        self._pro.kill()


class BaseAccountTests(BaseTest):

    def __init__(self, *args, **kwargs):
        super(BaseAccountTests, self).__init__(*args, **kwargs)
        self.username = ''
        self.password = ''
        self.token = ''

    def setUp(self):
        super(BaseAccountTests, self).setUp()

        end_point = f'http://localhost:{self._conf["Port"]}/login'
        data = json.dumps({
            'username': f'{self.username}',
            'password': f'{self.password}'
        }).encode('utf-8')
        method = 'POST'
        headers = {
            'Content-Type': 'application/json'
        }
        req = request.Request(end_point, data=data, headers=headers, method=method)

        try:
            f = request.urlopen(req)
            data = json.loads(f.read().decode('utf-8'))
            self.assertTrue('access_token' in data)
            self.token = data['access_token']
        except error.HTTPError as err:
            self.fail(err)
        else:
            pass


class _IntermediateServer:
    def __init__(self, tester):
        self._tester = tester
        self._conf = config.get_config('server')
        self.token = ''
        self._sio = Client(reconnection_delay=1, reconnection_attempts=2)

    def connect(self):
        req = webapi.build_request(
            'login',
            'POST',
            data={'username': 'intermediate_server',
                  'password': 'sufst'},
            content_type='application/json'
        )

        try:
            f = request.urlopen(req)
            data = json.loads(f.read().decode('utf-8'))
            self._tester.assertTrue('access_token' in data)
            self.token = data['access_token']
        except error.HTTPError as err:
            self._tester.fail(err)
        else:
            pass

        self._sio.connect(f'http://localhost:{self._conf["Port"]}',
                          headers={"Authorization": "Bearer " + self.token},
                          namespaces=['/car'])

        self._tester.assertTrue(self._sio.connected)

    @property
    def sio(self):
        return self._sio


class BaseAccountSocketIoTest(BaseAccountTests):
    def __init__(self, *args, **kwargs):
        super(BaseAccountSocketIoTest, self).__init__(*args, **kwargs)
        self._sio = None
        self._is = None

    def setUp(self):
        super(BaseAccountSocketIoTest, self).setUp()

        self._sio = Client(reconnection_attempts=5, reconnection_delay=1)
        self._sio.connect(f'http://localhost:{self._conf["Port"]}',
                          headers={"Authorization": "Bearer " + self.token},
                          namespaces=['/car'])

        self.assertTrue(self._sio.connected)

        self._is = _IntermediateServer(self)
        self._is.connect()

    def tearDown(self):
        self._sio.disconnect()
        self._is.sio.disconnect()

        super(BaseAccountSocketIoTest, self).tearDown()

