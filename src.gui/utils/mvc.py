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
import functools
import inspect
# from pubsub import pub
import sys
import types
import weakref
import wx
from wx.lib.pubsub import pub

from utils.doout import doout


class DynBindSlave(object):
    def __init__(self, name):
        self._dynbinding = list()
        self._dynbinding.append(name)

    def __getattribute__(self, name):
        _dynbinding = object.__getattribute__(self, '_dynbinding')
        if name == '_dynbinding':
            return _dynbinding
        _dynbinding.append(name)
        return self

    def __call__(self, func):
        curbinding = getattr(func, '_dynbinding', None)
        if curbinding is None:
            func._dynbinding = list()

        func._dynbinding.append(self._dynbinding[:])
        return func


class MetaDynBind(type):
    def __getattribute__(cls, name):
        return DynBindSlave(name)


class DynBind(object):
    __metaclass__ = MetaDynBind


def _reload_modules(cls, reloading=True):
    assert doout('called with', cls, 'reloading:', reloading)
    results = list()
    for modname in cls._moddirs:
        doout('cls.__module__', cls.__module__)
        doout('modname', modname)
        doout('cls.__name__', cls.__name__)

        clsmodname = cls.__module__.split('.')
        if len(clsmodname) > 1:
            clsmodname = '.'.join(clsmodname[:-1])
        else:
            clsmodname = cls.__module__

        clssubmodname = (clsmodname + '.' + modname +
                         '.' + cls.__name__.lower())
        doout('clssubmodname is', clssubmodname)

        try:
            clssubmod = sys.modules[clssubmodname]
        except KeyError, e:
            doout('KeyError on module fetch', e)
            results.append(e)
        else:
            load_submodule(cls, clssubmod, reloading, results)

    if reloading:
        for instance in cls._instances:
            instance._subscribe()
            instance._unbindfuncs()
            instance._bindfuncs()

    return results


def load_submodule(cls, submod, reloading, results):
    load_methods(cls, submod, reloading)

    if hasattr(submod, '__package__'):
        doout('submod.__package_', submod.__package__)
        doout('submod.__name__', submod.__name__)
        if submod.__package__ and submod.__package__ == submod.__name__:
            doout('loading package', submod.__name__)
            load_package(cls, submod, reloading, results)


def load_package(cls, package, reloading, results):
    for modname in dir(package):
        if modname.startswith('_'):
            continue

        mod = getattr(package, modname)
        if not isinstance(mod, types.ModuleType):
            continue

        doout('checking', modname)
        try:
            reload(mod)
        except ImportError, e:
            results.append(e)
        except Exception, e:
            results.append(e)
        else:
            # FIXME: need to refresh the reference to mod?
            # mod = getattr(module, modname)
            doout('loading submodule', mod.__name__)
            load_submodule(cls, mod, reloading, results)


def load_methods(cls, module, reloading):
    def fgetter(funcname):
        def fgetterreal(owner, *args, **kwargs):
            return owner._dynmethods[funcname](owner, *args, **kwargs)
        return fgetterreal

    for funcname in dir(module):
        if funcname.startswith('_') and funcname is not '__init__':
            continue

        func = getattr(module, funcname)
        if not isinstance(func, types.FunctionType):
            continue

        if funcname is '__init__':
            cls._dyninits[module] = func
            continue

        newfunc = funcname not in cls._dynmethods
        cls._dynmethods[funcname] = func
        if not reloading or newfunc:
            funcgetter = fgetter(funcname)
            funcgetter._pubrecv = getattr(func, '_pubrecv', None)
            funcgetter._dynbinding = getattr(func, '_dynbinding', None)
            setattr(cls, funcname, funcgetter)


def _unbindfuncs(self):
    # I would need a list of the functions that been bound to unbind them
    while True:
        try:
            widget, event, dynboundmethod = self._dynbindings.pop()
        except IndexError:
            break  # no more items in the list
        else:
            if event in [wx.EVT_MENU, wx.EVT_TOOL]:
                self.Unbind(event, handler=dynboundmethod, id=widget.GetId())
            elif event in [wx.EVT_SIZE]:
                self.Unbind(event, handler=dynboundmethod)
            else:
                widget.Unbind(event, handler=dynboundmethod)


def _bindfuncs(self):
    # wx classes throw exception if getmember is applied to the instance (self)
    methods = inspect.getmembers(self.__class__, inspect.ismethod)
    for mname, method in methods:
        dynbindings = getattr(method, '_dynbinding', None)
        if dynbindings is None:
            continue
        for dynbinding in dynbindings:
            if dynbinding:
                eventname, widgetprefix, widgetname = dynbinding
                event = getattr(wx, eventname, None)
                if event is None:
                    print 'Method', mname
                    print 'Failed to find eventname', eventname
                    continue

                name = 'm_' + widgetprefix.lower() + widgetname.lower()
                widget = None
                for attrname in dir(self):
                    if attrname.lower() == name:
                        widget = getattr(self, attrname)
                        break

                if not widget:
                    print 'Method', mname
                    print 'Failed to find widget', name
                    continue

                boundmethod = method.__get__(self, self.__class__)
                self._dynbindings.append((widget, event, boundmethod))
                if event in [wx.EVT_MENU, wx.EVT_TOOL]:
                    self.Bind(event, boundmethod, id=widget.GetId())
                elif event in [wx.EVT_SIZE]:
                    self.Bind(event, boundmethod)
                else:
                    widget.Bind(event, boundmethod)


def _inits(self, *args, **kwargs):
    for module, init in self._dyninits.iteritems():
        # Module could be helpful in debugging
        init(self, *args, **kwargs)


def _subscribe(self):

    def sgetter(funcname):
        def realsgetter(owner, msg):
            return owner._subs[funcname](owner, msg)
        return realsgetter

    # wx classes throw exception if getmember is applied to the instance (self)
    methods = inspect.getmembers(self.__class__, inspect.ismethod)
    topicmgr = pub.getDefaultTopicMgr()
    for mname, method in methods:
        pubsubtopic = getattr(method, '_pubrecv', None)
        if pubsubtopic:
            self._subs[mname] = method
            subsgetter = sgetter(mname)
            if (not topicmgr.getTopic(pubsubtopic, True) or
                not pub.isSubscribed(subsgetter, pubsubtopic)):

                setattr(self, mname, subsgetter)
                pub.subscribe(subsgetter.__get__(self, self.__class__),
                              pubsubtopic)


def DynamicClass(moddirs=None):
    if not moddirs:
        moddirs = ['.', 'mods', 'modules']

    def ClassWrapper(cls):
        def _getview(self):
            return self
        cls.view = property(_getview)

        cls._inits = _inits
        cls._subscribe = _subscribe
        cls._bindfuncs = _bindfuncs
        cls._unbindfuncs = _unbindfuncs

        _basecls = cls.__bases__[0]
        if _basecls is not object:
            _baseoldinit = _basecls.__init__

            def _basenewinit(self, *args, **kwargs):
                _baseoldinit(self, *args, **kwargs)
                self._inits(*args, **kwargs)

            _basecls.__init__ = _basenewinit

        def _newinit(self, *args, **kwargs):
            cls._instances.add(self)
            self._subs = dict()
            self._subscribe()
            _oldinit(self, *args, **kwargs)
            self._dynbindings = list()
            self._bindfuncs()

        _oldinit, cls.__init__ = cls.__init__, _newinit

        cls._instances = weakref.WeakSet()
        cls._dynmethods = dict()
        cls._dyninits = dict()
        cls._moddirs = moddirs
        cls._reload_modules = classmethod(_reload_modules)
        cls._reload_modules(reloading=False)

        return cls

    return ClassWrapper


def PubRecv(topic):
    def decorate(func):
        func._pubrecv = topic
        return func
    return decorate


def PubSend(topic, queue=True):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            msg = func(self, *args, **kwargs)
            if queue:
                wx.CallAfter(pub.sendMessage, topic, msg=msg)
            else:
                pub.sendMessage(topic, msg=msg)
        return wrapper
    return decorate
