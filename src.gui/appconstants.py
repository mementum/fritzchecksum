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
import sys

AppName = 'fritzchecksum'
VendorName = AppName
AppId = 'bb5f0e06-11e6-4ecd-8c0c-e5565d21fa34'
AppPublisher = 'Author'
AppURL = 'http://github.com/' + AppPublisher.lower() + '/' + AppName.lower()
AppExeName = AppName
AppYear = '2016'
AppExeType = 'onefile'  # 'onedir' or 'onefile'

AppTitle = AppName
AppVersion = '0.0.3'
AppSingleInstance = True
AppUACAdmin = False
AppUACUiAccess = False
AppUACManifest = False
AppConsole = False
AppPyOptimize = False

# Documents to be displayed in tabs in the About Dialog
about_datas = [
    ('README.rst', 'appdir'),
    ('LICENSE', 'appdir'),
    ('LICENSE-3rd', 'appdir'),
]

# Will be copied alongside the executable in onefile mode
copy_datas = {
    # relative dir from application root, [item_list]
    '.': ['README.rst', 'LICENSE', 'LICENSE-3rd'],
}

# Will be added to executable/collect as a TOC
toc_datas = {
    # relative dir from application root, [item_list]
    'icons': ['./src.gui/icons'],
}


def appisfrozen():
    return getattr(sys, 'frozen', False)


# Application and Data Directory functions
# '.' is usually the src/main.pyw directory
# if "icons" (example) are located one level upwards then use '..'
DATABASE = '.'


def getdatadir(abspath=False):
    if appisfrozen():
        # Running in a PyInstaller Bundle
        datadir = sys._MEIPASS
    else:
        # Running from source, datafiles are one level upwards
        datadir = os.path.join(os.path.dirname(sys.argv[0]), DATABASE)
    if abspath:
        datadir = os.path.abspath(datadir)
    return os.path.normpath(datadir)


def getdatapath(path, abspath=False):
    datadir = getdatadir(abspath=abspath)
    datapath = os.path.join(datadir, path)
    return os.path.normpath(datapath)

APPBASE = '..'


def getappdir(abspath=False):
    appdir = os.path.dirname(sys.argv[0])
    if not appisfrozen():
        # Running from source (root application dir located one level upwards)
        appdir = os.path.join(appdir, APPBASE)

    if abspath:
        appdir = os.path.abspath(appdir)
    return os.path.normpath(appdir)


def getapppath(path, abspath=False):
    appdir = getappdir(abspath=abspath)
    apppath = os.path.join(appdir, path)
    return os.path.normpath(apppath)
