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

"""Tests for timeline."""

from __future__ import absolute_import, print_function

from unittest import TestLoader


def test_suite():
    test_mod_names = [
        'timeline',
        'timedaction',
        'nestingtimedaction',
        'wsgi',
        ]
    return TestLoader().loadTestsFromNames(
        ['timeline.tests.test_' + name for name in test_mod_names])
