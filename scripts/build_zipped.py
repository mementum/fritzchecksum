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
import argparse
import logging
import sys

logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO)

if True:  # to avoid PEP-8 complains
    import build_utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prepare spec file and generate executable')
    args = parser.parse_args()

    logging.info('Creating Application Information Object')
    try:
        appinfo = build_utils.AppInfo()
    except Exception, e:
        logging.error('Failed to initialize AppInfo')
        logging.error(str(e))
        sys.exit(1)

    logging.info('Begin operations')
    logging.info(('Making (deleting if needed) previous executable '
                  'generation directories'))
    try:
        appinfo.make_dirs_zip()
    except OSError, e:
        logging.error('Directory operation failed')
        logging.error(str(e))
        sys.exit(1)

    logging.info('Creating zipfile')
    try:
        appinfo.zip_exe_dist()
    except Exception, e:
        logging.error('Zipfile operations failed')
        logging.error(str(e))
        sys.exit(1)

    logging.info('End of operations')
