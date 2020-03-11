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

from timeline.timedaction import TimedAction
from timeline.timeline import Timeline


class TestTimedAction(testtools.TestCase):

    def test_starts_now(self):
        action = TimedAction("Sending mail", None)
        self.assertIsInstance(action.start, datetime.datetime)

    def test_finish_sets_duration(self):
        action = TimedAction("Sending mail", None)
        self.assertEqual(None, action.duration)
        action.finish()
        self.assertIsInstance(action.duration, datetime.timedelta)

    def test__init__sets_category(self):
        action = TimedAction("Sending mail", None)
        self.assertEqual("Sending mail", action.category)

    def test__init__sets_detail(self):
        action = TimedAction(None, "fred.jones@example.com")
        self.assertEqual("fred.jones@example.com", action.detail)

    def test_logTuple(self):
        timeline = Timeline()
        action = TimedAction("foo", "bar", timeline)
        # Set variable for deterministic results
        action.start = timeline.baseline + datetime.timedelta(0, 0, 0, 2)
        action.duration = datetime.timedelta(0, 0, 0, 4)
        log_tuple = action.logTuple()
        self.assertEqual(5, len(log_tuple), "!= 5 elements %s" % (log_tuple,))
        # The first element is the start offset in ms.
        self.assertIsInstance(log_tuple[0], int)
        self.assertEqual(2, log_tuple[0])
        # The second element is the end offset in ms.
        self.assertIsInstance(log_tuple[1], int)
        self.assertEqual(6, log_tuple[1])
        self.assertEqual("foo", log_tuple[2])
        self.assertEqual("bar", log_tuple[3])
        # The fifth element defaults to None:
        self.assertEqual(None, log_tuple[4])

    def test_logTupleIncomplete(self):
        # Things that start and hit a timeout *may* not get recorded as
        # finishing in normal operation - they still need to generate a
        # logTuple, using now as the end point.
        timeline = Timeline()
        action = TimedAction("foo", "bar", timeline)
        # Set variable for deterministic results
        action.start = timeline.baseline + datetime.timedelta(0, 0, 0, 2)
        action._interval_to_now = lambda: datetime.timedelta(0, 0, 0, 3)
        log_tuple = action.logTuple()
        self.assertEqual(5, len(log_tuple), "!= 5 elements %s" % (log_tuple,))
        self.assertIsInstance(log_tuple[0], int)
        self.assertEqual(2, log_tuple[0])
        self.assertIsInstance(log_tuple[1], int)
        self.assertEqual(5, log_tuple[1])
        self.assertEqual("foo", log_tuple[2])
        self.assertEqual("bar", log_tuple[3])

    def test_logTupleBacktrace(self):
        # If the action has a backtrace attribute, that is placed into the
        # fifth element of logTuple.
        timeline = Timeline()
        action = TimedAction("foo", "bar", timeline)
        action.finish()
        action.backtrace = "Foo Bar"
        log_tuple = action.logTuple()
        self.assertEqual("Foo Bar", log_tuple[4])
