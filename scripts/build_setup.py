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
import subprocess
import sys

logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO)

import build_utils

iscc_cmd = ['iscc']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prepare iss file and build setup file')
    parser.add_argument('--iss',
                        action='store_true',
                        help='do only prepare the iss file')
    args = parser.parse_args()

    logging.info('Creating Application Information Object')
    try:
        appinfo = build_utils.AppInfo()
    except Exception, e:
        logging.error('Failed to initialize AppInfo')
        logging.error(str(e))
        sys.exit(1)

    logging.info('Checking AppId')
    retval, uuid = appinfo.validappid()
    if not retval:
        logging.error(('The application has not yet defined an Application'
                       ' UUID and the setup cannot be generated'))
        logging.error('Please add AppId="%s" to your appconstants file', uuid)
        sys.exit(1)

    logging.info('Getting the InnoSetup file')
    issfile = appinfo.getissfile()
    if not issfile:
        logging.error('iss file was not found. Check for presence')
        sys.exit(1)

    logging.info('Adjusting values in iss file')
    try:
        appinfo.prepare_issfile()
    except Exception, e:
        logging.error('Operation failed')
        logging.error(str(e))
        sys.exit(1)

    if args.iss:
        logging.info('Generated iss file. Setup build not requested. Exiting')
        sys.exit(0)

    logging.info('Checking executable distribution directories')
    if not appinfo.check_dirs_exe_dist():
        logging.error('Failed to find executable distribution dir. Exiting')
        sys.exit(1)

    logging.info('Creating (deleting if needed) the directories for setup')
    try:
        appinfo.make_dirs_setup()
    except OSError, e:
        logging.error('Directory operation failed')
        logging.error(str(e))
        sys.exit(1)

    logging.info('Copying distributable files from exec distribution dir')
    appinfo.copy_exedist_to_setupbuild()

    logging.info('Appending issfile %s to command line arguments to iscc' %
                 issfile)
    iscc_cmd.append(issfile)
    logging.info('Generating executable with command: %s' % ' '.join(iscc_cmd))
    subprocess.call(iscc_cmd)

    logging.info('End of operations')
