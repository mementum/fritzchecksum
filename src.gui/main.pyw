#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
################################################################################
#
# Copyright (C) 2014 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import utils.flushfile

import appconstants
import uimods.mainframe as mainframe
import utils.admin
import utils.artprovider
import utils.systemmenu
import sys
import win32gui
import wx


class MainApp(wx.App):
    def OnInit(self):
        # Admin Check
        retval, errmsg = utils.admin.CheckAdminRun()
        if not retval:
            wx.MessageBox(
                'This application needs Administrator permissions to run\n'
                '\n'
                'The following error happened:\n'
                '\n'
                '%s' % errmsg, 'Error')
            sys.exit(1)

        # Single Instance Check
        if appconstants.AppSingleInstance:
            self.instancename = '%s-%s' % (appconstants.AppName, wx.GetUserId())
            self.instance = wx.SingleInstanceChecker(self.instancename)
            if self.instance.IsAnotherRunning():
                wx.MessageBox("Another instance is already running", "Error")
                sys.exit(1)

        # Initialize and install an ArtProvider to fetch images
        artprovider = utils.artprovider.MyProvider()
        wx.ArtProvider.Push(artprovider)

        # Set App/Vendor Names for Config
        self.SetAppName(appconstants.AppName)
        self.SetVendorName(appconstants.VendorName)

        # Get/Create a Global Config Object
        # Check inifile presence
        inipath = appconstants.getapppath(appconstants.AppName + '.ini', abspath=True)
        try:
            f = open(inipath, 'rb')
        except IOError:
            # let the platform decide what and where
            config = wx.ConfigBase.Get()
        else:
            f.close()
            # portable
            config = wx.FileConfig(appName=appconstants.AppName,
                                   vendorName=appconstants.VendorName,
                                   localFilename=inipath,
                                   # globalFilename='',
                                   style=wx.CONFIG_USE_LOCAL_FILE)
            wx.ConfigBase.Set(config)

        config.SetRecordDefaults(True)

        # Send Logging to StdError
        wx.Log_SetActiveTarget(wx.LogStderr())
        # wx.Log_SetActiveTarget(wx.LogBuffer())

        # Create the frame
        self.view = mainframe.MainFrame(parent=None)
        if False:
            if not appconstants.appisfrozen():
                # Add system menuentry
                if not utils.systemmenu.AddSystemReloadMenu(self.view):
                    wx.MessageBox('Could not install system menu', 'Error')

        title = appconstants.AppTitle + ' - ' + appconstants.AppVersion
        self.view.SetTitle(title)

        # Set the top window - no longer needed in recent wxPython versions
        # self.SetTopWindow(self.view)
        # self.view.SetFocus()
        self.view.SetMinSize(self.view.GetSizer().GetMinSize())
        self.view.Fit()
        self.view.Show()
        self.view.Raise()

        return True

if __name__ == '__main__':
    # Run App avoiding redirection of errors to popup
    app = MainApp(redirect=False)
    app.MainLoop()
