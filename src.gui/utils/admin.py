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
import appconstants
import os
import os.path
import pywintypes
import time
import sys

if not appconstants.appisfrozen() and sys.platform == 'win32':
    # PyInstaller 3.0 (2015-10-27) cannot cope win32com.shell.shell
    # Import the modules below only if app is not frozen and win32
    # For an already built-in binary ... the manifest must be used
    import win32con
    import win32com.shell.shell
    import win32com.shell.shellcon

CheckRunAdminError = '''
Error, This application should be running as Administrator via
the embedded manifest.xml, but it is not.

The application needs administrator permissions to run.
'''


def CheckAdminRun():
    if not appconstants.AppUACAdmin or UserIsAdmin():
        # if admin not needed or already admin ... go ahead
        return True, None

    if not appconstants.appisfrozen() or sys.platform != 'win32':
        # Manifest cannot be used if not frozen or in unix-like systems
        return RunAsAdmin()
    elif not appconstants.AppUACManifest:
        # frozen and win32 ... and no manifest
        return RunAsAdmin()
    else:
        # frozen win32 ... and manifest
        # we "must" be running as Admin, becasue if not the application
        # would not have started
        # (or else ... a bug in the manifest or embedding process has acted)
        return False, ('Unknown error. Manifest must request Administrator'
                       ' permissions before launch')


def UserIsAdmin():
    if sys.platform == 'win32':
        return UserIsAdminWin32()

    return UserIsAdminUnixLike()


def UserIsAdminWin32():
    try:
        isadmin = win32com.shell.shell.IsUserAnAdmin()
    except pywintypes.error:
        isadmin = False  # assumption

    return isadmin


def UserIsAdminUnixLike():
    return os.getuid() == 0


def RunAsAdmin():
    if UserIsAdmin():
        # nothing to do ... already admin
        return True, None

    if sys.platform == 'win32':
        return RunAsAdminWin32()
    else:
        return RunAsAdminUnixLike()


def RunAsAdminWin32():
    # FIXME ... what happens if "frozen"
    script = os.path.abspath(sys.argv[0])
    if sys.executable != script:
        params = ' '.join([script] + sys.argv[1:])
    else:
        params = ' '.join(sys.argv[1:])

    # fMask = 0
    fMask = win32com.shell.shellcon.SEE_MASK_NO_CONSOLE
    # fMask=win32com.shell.shellcon.SEE_MASK_NOCLOSEPROCESS
    try:
        win32com.shell.shell.ShellExecuteEx(
            nShow=win32con.SW_SHOWNORMAL,
            fMask=fMask,
            lpVerb='runas',
            lpFile=sys.executable,
            lpParameters=params)
    except pywintypes.error, e:
        return False, e[2]

    # If ShellExecuteEx was ok ... this will never be reached
    # return True, None
    # In any case exit to avoid a "single instance check" failure
    sys.exit(0)


def RunAsAdminUnixLike():
    # FIXME ... what happens if "frozen"
    script = os.path.abspath(sys.argv[0])

    params = [sys.executable]
    if sys.executable != script:
        params.append(script)
        # CHECK Seems logic to always extend
        params.extend(sys.argv[1:])

    # FIXME ... execute the command directly
    try:
        os.execvp('sudo', params)
    except Exception, e:
        return False, str(e)

    # If execvp was ok ... this will never be reached
    return True, None
