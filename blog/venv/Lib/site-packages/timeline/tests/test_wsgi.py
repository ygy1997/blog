# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests of the WSGI integration."""

from __future__ import absolute_import, print_function

import testtools

from timeline.timeline import Timeline
from timeline.wsgi import make_app


class TestMakeApp(testtools.TestCase):

    def test_app_passes_through_setting_environ_variable(self):
        environ = {'foo': 'bar'}
        expected_start_response = object()
        expected_result = object()
        def inner_app(environ, start_response):
            self.assertIsInstance(environ['timeline.timeline'], Timeline)
            self.assertEqual(expected_start_response, start_response)
            self.assertEqual('bar', environ['foo'])
            return expected_result
        app = make_app(inner_app)
        self.assertEqual(
            expected_result, app(environ, expected_start_response))
