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
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import binascii
import io
import re

from . import py3


class ExportFile(object):
    '''Class to encapsulate the parsing of an export file and overwriting of
    the CRC value

    After loading a file it keeps the loaded content in an internal ``fout``
    '''

    ST_OK, ST_ERROR = True, False

    status = ST_ERROR  # until something is loaded
    error = None

    oldcrc = None
    newcrc = None

    fout = None

    def load(self, fin, out=True):
        '''
        Loads from a file-like/string object ``fin`` and will update internal
        ``status``, ``error``, ``oldcrc`` and ``newcrc``

        if ``out`` is ``False`` no internal buffering of the loaded input will
        be made

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception
        '''
        if isinstance(fin, py3.string_types):
            try:
                fin = io.open(fin, 'r')
            except IOError as e:
                self.status = self.ST_ERROR
                self.error = e
                return self.status, self.error

        return self.load_file(fin, out)

    def load_file(self, fin, out=True):
        '''
        Loads from a file-like object ``fin`` and will update internal
        ``status``, ``error``, ``oldcrc`` and ``newcrc``

        if ``out`` is ``False`` no internal buffering of the loaded input will
        be made

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception
        '''
        if out:
            self.fout = io.StringIO(newline='')
        self.oldcrc, self.newcrc = calc_crc32(fin, self.fout)

        self.status = self.ST_ERROR if self.oldcrc is None else self.ST_OK
        self.error = None if self.status == self.ST_OK else self.newcrc
        return self.status, self.error

    def save(self, fout):
        '''
        Writes the internal ``self.fout`` file to a file-like/string ``fout``

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception
        '''
        if self.status == self.ST_ERROR:
            return self.status, self.error

        if self.fout is None:
            return False, ValueError('No input buffering was made')

        if isinstance(fout, py3.string_types):
            try:
                fout = io.open(fout, 'w', newline='')
            except IOError as e:
                self.error = e
                self.status = self.ST_ERROR
                return self.status, self.error

            return self.save_file(fout)

    def save_file(self, fout):
        '''
        Writes the internal ``self.fout`` file to a file-like object ``fout``

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception
        '''
        if self.status == self.ST_ERROR:
            return self.status, self.error

        if self.fout is None:
            return False, ValueError('No input buffering was made')

        try:
            self.fout.seek(0)
            fout.write(self.fout.getvalue())
        except IOError as e:
            self.error = e
            self.status = self.ST_ERROR
            return self.status, self.error  # could be skipped in this case

        return self.status, self.error


def log_null(*args, **kwargs):
    pass


def calc_crc32(fin, fout=None, logcb=log_null):
    '''Calculates the CRC of a Fritz!Box configuration export file and writes
    the new CRC sum to a new configuration file

    Accepts:

      - fin: a file-like
      - fout: None or a file-like object. If a file, then the input will be
        written to the output with the new calculated CRC
      - logcb (default: log_null -> empty stub
        a logger which must a accepts *args (print will work)

    Returns:

      (oldcrc, newcrc) -> tuple

      oldcrc and newcrc will be strings representing a CRC32 in hexadecimal
      format if everything went fine

      oldcrc can be ``None`` which means an ``IOError`` exception has been
      raised and the operation has not completed successfully. In that case
      the 2nd value in the tuple contains the raised exception

    Note: the escape character '\' is escaped iself in some of the
    lines. CRC calculation will be wrong if the character is not
    un-escaped.

    The file is composed of the following:

      - A global "CONFIGURATION EXPORT" section

        Some variables (a=b) may be defined at this level. This definition
        contributes to the the CRC calculation by concatenating a and b and
        null terminating the result.

      - Subsections:

        The name (null terminated) of the subsection contributes to the CRC
        calculation

        - XXXBINFILE Section

          Lines represent hexadecimal values. The values (binary converted)
          are used directly in the calculation of the CRC (stripping eol
          before)

        - CFGFILE Section

          It is a textfile embedded in the larger export file. All lines
          including '\n' contribute to the CRC except the last line which
          must be stripped of the EOL character before being included in
          the CRC calculation

    '''
    NULLCHAR = '\0'  # shorthand for null termi

    # Regular expressions to parse lines
    RE_ROOT = re.compile(r'^\*+.+CONFIGURATION EXPORT.*')
    RE_ENDROOT = re.compile(r'^\*+\s+END OF EXPORT\s+(\w+)\s+\*+.*')
    RE_DEFROOT = re.compile(r'^(\w+)\s*=\s*([\$\.\w]+)\s*.*')  # root var def
    RE_BINFILE = re.compile(r'^\*+\s+\w*BINFILE:\s*([\w\.]+)\s*.*')
    RE_CFGFILE = re.compile(r'^\*+\s+CFGFILE:\s*([\w\.]+)\s*.*')
    RE_ENDFILE = re.compile(r'^\*+\s+END OF FILE\s+\*+.*')  # for all files

    # Statuses for the simple finite state machine
    ST_NONE, ST_ROOT, ST_CFGFILE, ST_BINFILE = range(4)

    status = ST_NONE
    crc = 0
    oldcrc = '0' * 8  # 8 x 4 -> 32 bits

    line = None
    while True:
        if fout is not None and line is not None:
            try:
                fout.write(line)
            except IOError as e:
                return None, e

        # Iterate lines manually to catch potential IOError exceptions
        try:
            line = next(fin)
        except StopIteration as e:
            break  # regular eof
        except IOError as e:
            return None, e  # error happen, notify it to caller

        logcb('Processing: {}'.format(line.rstrip('\n')))

        # No error/eof -> proceed
        # changin eol is not strictly needed but avoids recalculating the CRC
        # in original files
        l = line.replace('\r\n', '\n')  # CRCs do also work
        l = line.replace('\\\\', '\\')  # undo escaping in the line

        if status == ST_NONE:  # main level, nothing seen yet
            m = RE_ROOT.match(l)
            if m:
                logcb('ROOT DETECTED')
                status = ST_ROOT  # move to root of export
                continue

        elif status == ST_ROOT:
            m = RE_ENDROOT.match(l)
            if m:
                logcb('ROOT END: {}'.format(m.group(1)))
                oldcrc = m.group(1)  # end of export - keep oldcrc
                break

            m = RE_DEFROOT.match(l)  # variable definitions at root level
            if m:
                logcb('ROOT DEF: {}={}'.format(m.group(1), m.group(2)))
                # root variable definition seen, add to crc
                # a=b -> a + b + '\0'
                tocrc = m.group(1) + m.group(2) + NULLCHAR
                crc = binascii.crc32(tocrc, crc) & 0xffffffff
                continue

            m = RE_BINFILE.match(l)
            if m:
                status = ST_BINFILE  # start of binfile
                tocrc = m.group(1) + NULLCHAR  # add to crc with null term
                crc = binascii.crc32(tocrc, crc) & 0xffffffff
                continue

            m = RE_CFGFILE.match(l)
            if m:
                logcb('CFGFILE: {}'.format(m.group(1)))
                status = ST_CFGFILE  # start of cfgfile, change status
                last_l = None  # initialize single line buffer
                tocrc = m.group(1) + NULLCHAR  # add to crc with null term
                crc = binascii.crc32(tocrc, crc) & 0xffffffff
                continue

        elif status == ST_BINFILE:
            m = RE_ENDFILE.match(l)
            if m:
                logcb('END BINFILE')
                status = ST_ROOT  # go back to root level
                continue

            # else ... binary hex line - convert skipping eol
            logcb('BINFILE: processing line')
            hexed = binascii.unhexlify(l[:-1])  # convert to binary anc crc
            crc = binascii.crc32(hexed, crc) & 0xffffffff
            continue

        elif status == ST_CFGFILE:
            # The last line has to be stripped of eol, '\n'. The only way
            # to do this is by buffering each line once until. When the end
            # of section is seen, the buffered line is the last one
            m = RE_ENDFILE.match(l)
            if m:
                logcb('END CFGFILE')
                if last_l is not None:  # only operate if on something
                    crc = binascii.crc32(last_l[:-1], crc) & 0xffffffff

                status = ST_ROOT  # back to root level
                continue

            # crc existing buffered line
            logcb('CFGFILE: processing line')
            if last_l is not None:  # do only operate on something
                crc = binascii.crc32(last_l, crc) & 0xffffffff

            last_l = l  # buffer the line just seen
            continue

    # replace the CRC in the last line
    newcrc = format(crc, '08X')
    line = line.replace(oldcrc, newcrc)
    if fout is not None:
        try:
            fout.write(line)
        except IOError as e:
            pass

    return oldcrc, newcrc  # return old, new crc (str format both)
