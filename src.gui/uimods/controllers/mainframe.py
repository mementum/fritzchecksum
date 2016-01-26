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
from uimods.aboutdialog import AboutDialog
from utils.mvc import DynBind, PubRecv
import utils.wxfb as wxfb
import wx

import models.mainmodel as mainmodel

if True:
    def __init__(self, parent):
        # maingui.MainFrame.__init__(self, parent)

        wxfb.BindingFilePicker('fileread')
        wxfb.BindingFilePicker('filewrite')

        wxfb.BindingButton('execute')
        self.model = mainmodel.MainModel()

if True:
    @PubRecv('evt_button.execute')
    def OnButtonExecute(self, msg):
        pread = self.fileread.path
        pwrite = self.filewrite.path

        if not pread:
            wx.MessageBox('No file to read', 'Error')
            return

        if not pwrite:
            wx.MessageBox('No file to write', 'Error')
            return

        self.model.execute(pread, pwrite)

if True:
    @DynBind.EVT_BUTTON.Button.AboutDialog
    @DynBind.EVT_TOOL.Tool.AboutDialog
    @DynBind.EVT_MENU.MenuItem.AboutDialog
    def OnEventAboutDialog(self, event):
        event.Skip()
        dialog = AboutDialog(self)
        dialog.ShowModal()
