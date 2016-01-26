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
import collections


class MutableSet(collections.MutableSet):
    def __init__(self, iterable=None, owner=None, instance=None):
        try:
            self._set = set(iterable)
        except TypeError:
            self._set = set()
        self.owner = owner
        self.instance = instance

    # Container -> Set -> MutableSet (Abstract Method)
    def __contains__(self, elem):
        return elem in self._set

    # Iterable -> Set -> MutableSet (Abstract Method)
    def __iter__(self):
        return iter(self._set)

    # Sized -> Set -> MutableSet (Abstract Method)
    def __len__(self):
        return len(self._set)

    def notify(self):
        if self.owner:
            self.owner.__set__(self.instance, self._set)

    # MutableSet (Abstract Method)
    def add(self, elem):
        self._set.add(elem)
        self.notify()

    # MutableSet (Abstract Method)
    def discard(self, elem):
        self._set.discard(elem)
        self.notify()


class MutableSequence(collections.MutableSequence):
    def __init__(self, iterable=None, owner=None, instance=None):
        try:
            self.seq = list(iterable)
        except TypeError:
            self.seq = list()
        self.owner = owner
        self.instance = instance

    # Sized -> Sequence -> MutableSequence (Abstract Method)
    def __len__(self):
        return len(self.seq)

    # Iterable -> Sequence -> MutableSequence (Abstract Method)
    def __iter__(self):
        return iter(self.seq)

    # Container -> Sequence -> MutableSequence (Abstract Method)
    def __contains__(self, elem):
        return elem in self.seq

    # MutableSequence (Abstract Method)
    def __getitem__(self, key):
        return self.seq[key]

    def notify(self):
        if self.owner:
            self.owner.__set__(self.instance, self.seq)

    # MutableSequence (Abstract Method)
    def __setitem__(self, key, value):
        self.seq[key] = value
        self.notify()

    # MutableSequence (Abstract Method)
    def __delitem__(self, key):
        del self.seq[key]
        self.notify()

    # MutableSequence (Abstract Method)
    def insert(self, key, value):
        self.seq.insert(key, value)
        self.notify()
