#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2016 Daniel Rodriguez
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
###############################################################################
import sys


PRINT_MESSAGES = False


if sys.platform != 'win32':
    def WndProcManage(wnd):
        return True

    def AddSystemReloadMenu(wnd):
        return True
else:
    import collections
    import win32api
    import win32gui
    import win32con

    def WndProcManage(wnd):
        if not hasattr(wnd, 'GetHandle'):
            return False

        # Make a dictionary of message names to be used for printing below
        if PRINT_MESSAGES:
            msgdict = dict()
            for name in dir(win32con):
                if name.startswith('WM_'):
                    value = getattr(win32con, name)
                    msgdict[value] = name

        _oldWndProc = win32gui.GetWindowLong(wnd.GetHandle(),
                                             win32con.GWL_WNDPROC)

        def MyWndProc(self, hwnd, msg, wParam, lParam):
            # Display what we've got.
            if PRINT_MESSAGES:
                print (msgdict.get(msg), msg, wParam, lParam)

            # Restore the old WndProc.  Notice the use of win32api
            # instead of win32gui here.  This is to avoid an error due to
            # not passing a callable object.
            if msg == win32con.WM_DESTROY:
                win32api.SetWindowLong(self.GetHandle(),
                                       win32con.GWL_WNDPROC,
                                       _oldWndProc)

            stopproc = False
            for cb, cbtrigger in CALLBACKS[self]:
                if cbtrigger(self, msg, wParam, lParam):
                    if not cb(self, msg, wParam, lParam):
                        stopproc = True
                        break

            if stopproc:
                return
            # Pass all messages (in this case, yours may be different) on to
            # the original WndProc
            return win32gui.CallWindowProc(_oldWndProc,
                                           hwnd, msg,
                                           wParam,
                                           lParam)

        # Bind the function to the passed object
        _newWndProc = MyWndProc.__get__(wnd, wnd.__class__)

        # Set the WndProc to our function
        win32gui.SetWindowLong(wnd.GetHandle(),
                               win32con.GWL_WNDPROC,
                               _newWndProc)
        return True

    CALLBACKS = collections.defaultdict(list)

    class CallbackTrigger(object):

        def __init__(self, wnd, msg, wparam, lparam):
            self.wnd = wnd
            self.msg = msg
            self.wparam = wparam
            self.lparam = lparam

        def __call__(self, wnd, msg, wparam, lparam):
            wn = (self.wnd.GetHandle() == wnd.GetHandle())
            ms = (self.msg == msg)
            wp = (self.wparam is None or self.wparam == wparam)
            lp = (self.lparam is None or self.lparam == lparam)

            return wn and ms and wp and lp

    def AddCallback(cb, wnd, msg, wparam=None, lparam=None):
        CALLBACKS[wnd].append((cb, CallbackTrigger(wnd, msg, wparam, lparam)))

    SYS_MENU_RELOAD_MODULES = 0xff01

    def AddSystemReloadMenu(wnd):
        if not WndProcManage(wnd):
            return False

        hSysMenu = win32gui.GetSystemMenu(wnd.GetHandle(), False)
        if not hSysMenu:
            return False
        win32gui.InsertMenu(hSysMenu,
                            0,
                            win32con.MF_BYPOSITION | win32con.MF_SEPARATOR,
                            0,
                            '')

        win32gui.InsertMenu(hSysMenu,
                            0,
                            win32con.MF_BYPOSITION,
                            SYS_MENU_RELOAD_MODULES,
                            'Reload Modules')

        def HandleSystemMenu(wnd, msg, wparam, lparam):
            wnd.__class__._reload_modules()
            return False

        AddCallback(HandleSystemMenu,
                    wnd,
                    win32con.WM_SYSCOMMAND,
                    SYS_MENU_RELOAD_MODULES,
                    None)
        return True
