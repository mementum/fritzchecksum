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


def calc_crc32(path_in, path_out):
    '''
    Calculates the CRC of a Fritz!Box configuration export file and writes the
    new CRC sum to a new configuration file

    Returns:

      (oldcrc, newcrc) -> tuple

      oldcrc and newcrc will be strings representing a CRC32 in hexadecimal
      format if everything went fine

      oldcrc can be ``None`` which means an ``IOError`` exception has been
      raised and the operation has not completed successfully. In that case the
      2nd value in the tuple contains the raised exception

    Note: the escape character '\' is escaped iself in some of the lines. CRC
    calculation will be wrong if the character is not un-escaped.

    The file is composed of the following:

      - A global "CONFIGURATION EXPORT" section

        Some variables (a=b) may be defined at this level. This definition
        contributes to the the CRC calculation by concatenating a and b and
        null terminating the result.

      - Subsections:

        The name (null terminated) of the subsection contributes to the CRC
        calculation

        - BINFILE Section

          Lines represent hexadecimal values. The values (binary converted) are
          used directly in the calculation of the CRC (stripping eol before)

        - CFGFILE Section

          It is a textfile embedded in the larger export file. All lines
          including '\n' contribute to the CRC except the last line which must
          be stripped of the EOL character before being included in the CRC
          calculation
    '''
    NULLCHAR = '\0'  # shorthand for values which must be null term'd for crc

    # Regular expressions to parse lines
    RE_ROOT = re.compile(r'\*+ (.+) CONFIGURATION EXPORT')
    RE_ENDROOT = re.compile(r'\*+ END OF EXPORT (\w+) \*+')
    RE_DEFROOT = re.compile(r'(\w+)=(.+)')  # variable definition at root level
    RE_BINFILE = re.compile(r'\*+ BINFILE:(.+)')
    RE_CFGFILE = re.compile(r'\*+ CFGFILE:(.+)')
    RE_ENDFILE = re.compile(r'\*+ END OF FILE \*+')  # common for cfg and bin

    # Statuses for the simple finite state machine
    ST_NONE, ST_ROOT, ST_CFGFILE, ST_BINFILE = range(4)

    try:
        fin = io.open(path_in, 'r', encoding='utf-8')
    except IOError as e:
        return (None, e)

    try:
        fout = io.open(path_out, 'w', encoding='utf-8')
    except IOError as e:
        return (None, e)

    status = ST_NONE
    crc = 0
    oldcrc = '0' * 8  # 8 x 4 -> 32 bits

    line = None
    while True:
        if line is not None:
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

        # No error/eof -> proceed
        l = line.replace('\\\\', '\\')  # undo escaping in the line

        if status == ST_NONE:  # main level, nothing seen yet
            m = RE_ROOT.match(l)
            if m:
                status = ST_ROOT  # move to root of export
                continue

        elif status == ST_ROOT:
            m = RE_ENDROOT.match(l)
            if m:
                oldcrc = m.group(1)  # end of export - keep oldcrc


                break

            m = RE_DEFROOT.match(l)  # variable definitions at root level
            if m:
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
                status = ST_CFGFILE  # start of cfgfile, change status
                last_l = None  # initialize single line buffer
                tocrc = m.group(1) + NULLCHAR  # add to crc with null term
                crc = binascii.crc32(tocrc, crc) & 0xffffffff
                continue

        elif status == ST_BINFILE:
            m = RE_ENDFILE.match(l)
            if m:
                status = ST_ROOT  # go back to root level
                continue

            # else ... binary hex line - convert skipping eol
            hexed = binascii.unhexlify(l[:-1])  # convert to binary anc crc
            crc = binascii.crc32(hexed, crc) & 0xffffffff
            continue

        elif status == ST_CFGFILE:
            # The last line has to be stripped of eol, '\n'. The only way to do
            # this is by buffering each line once until. When the end of
            # section is seen, the buffered line is the last one
            m = RE_ENDFILE.match(l)
            if m:
                if last_l is not None:  # do only operate if something is there
                    crc = binascii.crc32(last_l[:-1], crc) & 0xffffffff

                status = ST_ROOT  # back to root level
                continue

            # crc existing buffered line
            if last_l is not None:  # do only operate on something
                crc = binascii.crc32(last_l, crc) & 0xffffffff

            last_l = l  # buffer the line just seen
            continue

    # replace the CRC in the last line
    newcrc = format(crc, 'x')
    line = line.replace(oldcrc, newcrc)
    fout.write(line)

    fin.close()
    fout.close()  # although going out of scope should close both files

    return oldcrc, newcrc  # return old, new crc (str format both)


if __name__ == '__main__':
    import sys
    cfgpath = sys.argv[1]
    oldcrc, newcrc = calc_crc32(cfgpath, cfgpath + '.out')
    print('old {} vs new {}'.format(oldcrc, newcrc))
