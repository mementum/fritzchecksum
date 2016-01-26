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
from wx import ListCtrl
from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin


class SortableListCtrl(ListCtrl, ColumnSorterMixin):

    def __init__(self, *args, **kwargs):
        # *args, **kwargs ensures it can be used with GUI builders unmodified
        ListCtrl.__init__(self, *args, **kwargs)
        # Initialize needed dictionary for ColumSorterMixin
        self.itemDataMap = dict()
        ColumnSorterMixin.__init__(self, 0)  # start with 0 columns

    # Method required by ColumnSorterMixin
    def GetListCtrl(self):
        return self

    # Overriden Methods to keep the right column count in ColumSorterMixin
    def InsertColumn(self, col, info):
        retval = ListCtrl.InsertColumn(self, *args, **kwargs)
        ColumnSorterMixin.SetColumnCount(self, self.GetColumnCount())
        return retval

    def DeleteColumn(self, col):
        retval = ListCtrl.DeleteColumn(self, col)
        ColumnSorterMixin.SetColumnCount(self, self.GetColumnCount())
        return retval

    def DeleteAllColumns(self):
        retval = ListCtrl.DeleteAllColumns(self)
        ColumnSorterMixin.SetColumnCount(self, self.GetColumnCount())
        return retval

    # Keep itemDataMap synchronized with Item Deletion
    def DeleteAllItems(self):
        self.itemDataMap.clear()
        return ListCtrl.DeleteAllItems(self)

    def DeleteItem(self, item):
        data = self.GetItemData(item)
        self.itemDataMap.pop(data, None)  # try to delete and avoid errors
        return ListCtrl.DeleteItem(item)

    # Build the entry for itemDataMap when setting the data for the item
    def SetItemData(self, item, data):
        retval = ListCtrl.SetItemData(self, item, data)

        datamap = list()
        for col in xrange(0, self.GetColumnCount()):
            listitem = self.GetItem(item, col)
            datamap.append(listitem.GetText())

        self.itemDataMap[item] = datamap
        return retval

    # Ensure that changes to column text are kept sync'ed in itemDataMap
    def SetStringItem(self, index, col, label):
        retval = ListCtrlMap.SetStringItem(self, index, col, label)
        data = self.GetItemData(index)
        if data:
            try:
                datamap = self.itemDataMap[data]
            except KeyError:
                datamap = [''] * self.GetColumnCount()
                self.itemDataMap[data] = datamap

            datamap[col] = label

        return retval
