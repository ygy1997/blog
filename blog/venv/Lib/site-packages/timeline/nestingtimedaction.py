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

"""Time an action which calls other timed actions."""


from __future__ import absolute_import, print_function

__all__ = ['NestingTimedAction']

__metaclass__ = type


import datetime

from timeline.timedaction import TimedAction


class NestingTimedAction(TimedAction):
    """A variation of TimedAction which creates a nested environment.
    
    This is done by recording two 0 length timed actions in the timeline:
    one at the start of the action and one at the end, with -start and
    -stop appended to their categories.

    See `TimedAction` for more information.
    """

    def _init(self):
        self.duration = datetime.timedelta()
        self._category = self.category
        self.category = self._category + '-start'

    def finish(self):
        """Mark the TimedAction as finished."""
        end = self.timeline.start(self._category + '-stop', self.detail)
        end.duration = datetime.timedelta()
