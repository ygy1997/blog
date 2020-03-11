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

"""Time a single categorised action."""


from __future__ import absolute_import, division, print_function

__all__ = ['TimedAction']

__metaclass__ = type


import datetime

import pytz


UTC = pytz.utc


class TimedAction:
    """An individual action which has been timed.

    :ivar timeline: The timeline that this action took place within.
    :ivar start: A datetime object with tz for the start of the action.
    :ivar duration: A timedelta for the duration of the action. None for
        actions which have not completed.
    :ivar category: The category of the action. E.g. "sql".
    :ivar detail: The detail about the action. E.g. "SELECT COUNT(*) ..."
    :ivar backtrace: A backtrace for when the action was started. Useful for
        detecting code paths that cause lots of actions (usually a bad thing
        from a performance perspective).
    """

    def __init__(self, category, detail, timeline=None):
        """Create a TimedAction.

        New TimedActions have a start but no duration.

        :param category: The category for the action.
        :param detail: The detail about the action being timed.
        :param timeline: The timeline for the action.
        """
        self.start = datetime.datetime.now(UTC)
        self.duration = None
        self.category = category
        self.detail = detail
        self.timeline = timeline
        self.backtrace = None
        self._init()

    def _init(self):
        # hook for child classes.
        pass

    def __repr__(self):
        return "<%s %s[%s]>" % (self.__class__, self.category,
            self.detail[:20])

    def logTuple(self):
        """Return a 4-tuple suitable for errorlog's use."""
        offset = self._td_to_ms(self.start - self.timeline.baseline)
        if self.duration is None:
            # This action wasn't finished: pretend it has finished now
            # (even though it hasn't). This is pretty normal when action ends
            # are recorded by callbacks rather than stack-like structures. E.g.
            # storm tracers in launchpad:
            # log-trace START : starts action
            # timeout-trace START : raises 
            # log-trace FINISH is never called.
            length = self._td_to_ms(self._interval_to_now())
        else:
            length = self._td_to_ms(self.duration)
        return (offset, offset + length, self.category, self.detail,
            self.backtrace)

    def _td_to_ms(self, td):
        """Tweak on a backport from python 2.7"""
        return (td.microseconds + (
            td.seconds + td.days * 24 * 3600) * 10**6) // 10**3

    def finish(self):
        """Mark the TimedAction as finished."""
        self.duration = self._interval_to_now()

    def _interval_to_now(self):
        return datetime.datetime.now(UTC) - self.start
