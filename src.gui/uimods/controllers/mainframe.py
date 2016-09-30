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
import os.path

import wx

from uimods.aboutdialog import AboutDialog
from utils.mvc import DynBind, PubRecv
import utils.wxfb as wxfb

import models.mainmodel as mainmodel

if True:
    def __init__(self, parent):
        pass
if True:
    @PubRecv('evt_filepicker_changed.fileread')
    def OnFilePickerChanged(self, msg):
        self.model.load(self.fileread.path)

if True:
    @PubRecv('evt_button.recalculate')
    def OnButtonRecalculate(self, msg):
        self.model.load(self.fileread.path)

if True:
    @PubRecv('evt_button.save')
    def OnButtonSave(self, msg):
        if not self.model.status:
            wx.MessageBox('No export file has been successfully loaded yet!')
            return

        ret = wx.MessageBox('Overwrite the original file?', 'Attention!',
                            wx.YES_NO | wx.ICON_QUESTION)

        if ret == wx.YES:
            self.model.save(self.fileread.path)

if True:
    @PubRecv('evt_button.saveas')
    def OnButtonSaveAs(self, msg):
        if not self.model.status:
            wx.MessageBox('No export file has been successfully loaded yet!')
            return

        dialog = wx.FileDialog(
            self, 'Save As ...', style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        result = dialog.ShowModal()
        if result != wx.ID_OK:
            return

        # Show filedialog and get value
        self.model.save(dialog.GetPath())

if True:
    @DynBind.EVT_BUTTON.Button.AboutDialog
    @DynBind.EVT_TOOL.Tool.AboutDialog
    @DynBind.EVT_MENU.MenuItem.AboutDialog
    def OnEventAboutDialog(self, event):
        event.Skip()
        dialog = AboutDialog(self)
        dialog.ShowModal()
