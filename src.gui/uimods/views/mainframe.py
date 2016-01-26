#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
#  Copyright (C) 2014 Daniel Rodriguez
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
from utils.mvc import PubRecv
import wx

if True:
    @PubRecv('model.executed')
    def On_ModelNextMotd(self, msg):
        oldcrc, newcrc = msg

        if oldcrc is None:
            wx.MessageBox(str(e), 'An error happened')
            return

        txt = 'OldCRC: {} - NewCRC: {}'.format(oldcrc, newcrc)
        wx.MessageBox(txt, 'CRC Calculation completed')
