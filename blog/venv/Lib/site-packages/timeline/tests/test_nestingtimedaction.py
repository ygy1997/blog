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

"""Tests of the TimedAction class."""

from __future__ import absolute_import, print_function

__metaclass__ = type

import datetime

import testtools

from timeline.nestingtimedaction import NestingTimedAction
from timeline.timeline import Timeline


class TestNestingTimedAction(testtools.TestCase):

    def test_finish_adds_action(self):
        timeline = Timeline()
        action = NestingTimedAction("Sending mail", None, timeline)
        action.finish()
        self.assertEqual(1, len(timeline.actions))
        self.assertEqual(datetime.timedelta(), timeline.actions[-1].duration)

    def test__init__sets_duration(self):
        action = NestingTimedAction("Sending mail", None)
        self.assertEqual(datetime.timedelta(), action.duration)
