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


import argparse

from . import checksum


def parse_args(pargs=''):
    parser = argparse.ArgumentParser(
        description='FritzChecksum Calculator/Overwriter',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument('--change', '-c',
                       action='store_true',
                       required=False,
                       help='Change CRC directly in input file')

    group.add_argument('--output', '-o',
                       action='store',
                       required=False,
                       default=None,
                       help='Write input to output with new CRC')

    parser.add_argument('input',
                        action='store',
                        help='Write input to output with new CRC')

    if pargs:
        return parser.parse_args(pargs.split())

    return parser.parse_args()


def run():
    args = parse_args()

    # Check if saving to a file has been requested
    ofile = None
    if args.change:
        ofile = args.input
    elif args.output is not None:
        ofile = args.output

    # Do the thing
    export = checksum.ExportFile()
    # Use ofile as flag to request load buffering input
    ret, error = export.load(args.input, ofile is not None)
    if not ret:
        print('An error has ocurred:', error)
        sys.exit(1)

    # Print oldcrc and newcrc
    print('{} -> {}'.format(export.oldcrc, export.newcrc))

    if ofile is not None:
        # Save to a file
        print('Saving to {}'.format(ofile))
        ret, error = export.save(ofile)

        if not ret:
            print('An error has ocurred:', error)
            sys.exit(1)
