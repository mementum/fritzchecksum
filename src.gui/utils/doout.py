#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
#  Copyright (C) 2016 Daniel Rodriguez
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import sys


def doout(*args):
    if False:
        frame = sys._getframe(1)
        funcname = frame.f_code.co_name
        if 'self' in frame.f_locals:
            funcname = \
                frame.f_locals['self'].__class__.__name__ + '.' + funcname

        print funcname, '(', args, ')'
    return True
