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

"""Coordinate a sequence of non overlapping TimedActionss."""

from __future__ import absolute_import, print_function

__all__ = ['Timeline']

__metaclass__ = type

import datetime
import sys
import traceback

from pytz import utc as UTC

from timeline.nestingtimedaction import NestingTimedAction
from timeline.timedaction import TimedAction


class OverlappingActionError(Exception):
    """A new action was attempted without finishing the prior one."""
    # To make analysis easy we do not permit overlapping actions by default:
    # each action that is being timed and accrued must complete before the next
    # is started. This means, for instance, that sending mail cannot do SQL
    # queries, as both are timed and accrued. OTOH it makes analysis and
    # serialisation of timelines simpler, and for the current use cases in 
    # Launchpad this is sufficient. This constraint should not be considered
    # sacrosanct - if, in future, we desire timelines with overlapping actions,
    # as long as the OOPS analysis code is extended to generate sensible
    # reports in those situations, this can be changed. In the interim, actions
    # can be explicitly setup to permit nesting by passing allow_nested=True
    # which will cause the action to be recorded with 0 duration and a -start
    # and -stop suffix added to its category. This is potentially lossy but
    # good enough to get nested metrics and can be iterated on in the future to
    # do an actual stacked/tree model of actions - if needed.


def format_stack():
    """Format a stack like traceback.format_stack, but skip 2 frames.

    This means the stack formatting frame isn't in the backtrace itself.
    """
    return traceback.format_stack(f=sys._getframe(2))


class Timeline:
    """A sequence of TimedActions.

    This is used for collecting expensive/external actions inside Launchpad
    requests.

    :ivar actions: The actions.
    :ivar baseline: The point the timeline starts at.
    """

    def __init__(self, actions=None, format_stack=format_stack):
        """Create a Timeline.
        
        :param actions: An optional object to use to store the timeline. This
            must implement the list protocol.
        :param format_stack: The helper to use when gathering tracebacks. If
            None tracebacks are not gathered. Must return a list of strings
            for concatenation.
        """
        if actions is None:
            actions = []
        self.actions = actions
        self.baseline = datetime.datetime.now(UTC)
        self.format_stack = format_stack

    def start(self, category, detail, allow_nested=False):
        """Create a new TimedAction at the end of the timeline.

        :param category: the category for the action.
        :param detail: The detail for the action.
        :param allow_nested: If True treat this action as a nested action -
            record it twice with 0 duration, once at the start and once at the
            finish.
        :return: A TimedAction for that category and detail.
        """
        if allow_nested:
            result = NestingTimedAction(category, detail, self)
        else:
            result = TimedAction(category, detail, self)
        if self.actions and self.actions[-1].duration is None:
            raise OverlappingActionError(self.actions[-1], result)
        self.actions.append(result)
        if self.format_stack is not None:
            result.backtrace = ''.join(self.format_stack())
        return result
