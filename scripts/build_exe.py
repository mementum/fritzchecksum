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

if True:  # to avoid PEP-8 complaints
    import build_utils

##################################################
# CONSTANTS FOR SPEC GENERATION
##################################################
# pyinstaller can generate spec and executable in one step
# specs_cmd = ['pyinstaller', '--noconfirm', '--windowed', '--noupx']

# Base command for spec generation
# --noconfirm is not accepted by pyi-makespec
specs_cmd = ['pyi-makespec', '--noupx']

# Base command for executable generation
pyinst_cmd = ['pyinstaller', '--noconfirm']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prepare spec file and generate executable')
    parser.add_argument('--clean', action='store_true',
                        help='tell pyinstaller to clean up the build cache')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--console', required=False, action='store_true',
                       help='Build the console application if present')

    group.add_argument('--gui', required=False, action='store_true',
                       help='Build the gui application if present')

    args = parser.parse_args()

    # Decide whether we are building console or gui
    gui = args.gui or not args.console

    logging.info('Creating Application Information Object')
    try:
        appinfo = build_utils.AppInfo(gui=gui)
    except Exception, e:
        logging.error('Failed to initialize AppInfo')
        logging.error(str(e))
        sys.exit(1)

    logging.info('Getting Spec file')
    specfile = appinfo.getspecfile()
    if not specfile:
        logging.error('Specfile was not found. Check for presence')
        sys.exit(1)

    logging.info('Begin operations')
    logging.info('Cleaning up backups')
    try:
        appinfo.clean_srcdir_backups()
    except OSError, e:
        logging.error('Failed to remove all backups')
        logging.error(str(e))
        sys.exit(1)

    logging.info('Cleaning up compiled pythons')
    try:
        appinfo.clean_srcdir_pyc()
    except OSError, e:
        logging.error('Failed to remove all compiled python files')
        logging.error(str(e))
        sys.exit(1)

    logging.info(('Making (deleting if needed) previous executable'
                  ' generation directories'))
    try:
        appinfo.make_dirs_exe()
    except OSError, e:
        logging.error('Directory operation failed')
        logging.error(str(e))
        sys.exit(1)

    if args.clean:
        logging.info('Adding --clean to command line arguments')
        pyinst_cmd.append('--clean')

    logging.info('Adding work directory to command line arguments')
    pyinst_cmd.append('--workpath=' + appinfo.dirs['exe_build'])
    logging.info('Adding distribution directory to command line arguments')
    pyinst_cmd.append('--distpath=' + appinfo.dirs['exe_dist'])
    logging.info('Adding specfile to command line arguments')
    pyinst_cmd.append(specfile)

    logging.info('Generating executable with command: %s' %
                 ' '.join(pyinst_cmd))
    subprocess.call(pyinst_cmd)

    logging.info('End of operations')
