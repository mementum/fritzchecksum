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
from utils.mvc import DynamicClass, PubSend


import fritzchecksum


@DynamicClass(moddirs=['modules'])
class MainModel(object):
    def __init__(self):
        self.export = fritzchecksum.ExportFile()

    @PubSend('model.loaded')
    def load(self, path):
        return self.export.load(path)

    @PubSend('model.saved')
    def save(self, path):
        return self.export.save(path)

    @property
    def crcold(self):
        return self.export.oldcrc

    @property
    def crcnew(self):
        return self.export.newcrc

    @property
    def status(self):
        return self.export.status
