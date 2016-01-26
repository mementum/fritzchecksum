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
import datetime
import filecmp
import fnmatch
import glob
import imp
import os
import os.path
import py_compile
import shutil
import sys
import tempfile
import uuid
import zipfile


# Line buffering is broken in Win32 platforms
# Running under cygwin/mingw32 this is needed to see a line
# show up when the print statement is issued
class flushfile(object):
    def __init__(self, f):
        self.f = f

    def write(self, x):
        self.f.write(x)
        self.f.flush()

if sys.platform == 'win32':
    sys.stdout = flushfile(sys.stdout)
    sys.stderr = flushfile(sys.stderr)

##################################################
# CONFIGURABLE VALUES
##################################################
appinfomodname = 'appconstants'

appdefaults = {
    'AppName': 'AppName',
    'VendorName': 'VendorName',
    'AppId': 'AppId',
    'AppPublisher': 'AppPublisher',
    'AppURL': 'http://appname.com/',
    'AppExeName': 'AppName',
    'AppYear': str(datetime.datetime.now().year),
    'AppExeType': 'onedir',  # 'onedir' or 'onefile'
    'AppTitle': 'AppName',
    'AppVersion': '0.0.1',
    'AppSingleInstance': True,
    'AppUACAdmin': False,
    'AppUACUiAccess': False,
    'AppUACManifest': False,
    'AppConsole': False,
    'AppPyOptimize': False,
    'copy_datas': dict(),
    'toc_datas': dict(),
}

inno_replace = ['AppName', 'AppVersion', 'AppPublisher',
                'AppYear', 'AppURL', 'AppExeName', 'AppId']
inno_dirs = {'BuildDir': 'setup_build', 'DistDir': 'setup_dist'}

clean_patterns = ['*~', '*.bak']
pyc_patterns = ['*.pyc', '*.pyo']
compile_patterns = ['*.py']

appdirs = [
    # dirname, basedir, dir relative path
    ('script', 'app', '.'),
    ('base', 'script', '..'),
    ('hooks', 'script', 'hooks'),
    ('src', 'base', 'src'),

    # Base Directory for binaries
    ('binaries', 'base', 'binaries'),

    # Executable Generation/Distribution Directories
    ('exe', 'binaries', 'exe'),
    ('exe_build', 'exe', 'build'),
    ('exe_dist', 'exe', 'dist'),

    # Setup Generation/Distribution Directories
    ('setup', 'binaries', 'setup'),
    ('setup_build', 'setup', 'build'),
    ('setup_dist', 'setup', 'dist'),

    # Zipped Generation/Distribution Directories
    ('zip', 'binaries', 'zip'),
    ('zip_dist', 'zip', 'zip_dist'),
]

appreldirs = [
    # Inno Setup needs relative paths to the script in the iss file
    ('setup_build', 'setup_build', 'script'),
    ('setup_dist', 'setup_dist', 'script'),
]


##################################################
# Operational object for Executable and Setup generation
##################################################
class AppInfo(object):

    def __init__(self, initdir=None, gui=True):
        self.gui = gui
        if not initdir:
            if getattr(sys, 'frozen', False):
                scriptname = sys.executable
            else:
                scriptname = sys.argv[0]
            initdir = os.path.dirname(scriptname)

        self.init_dirs(initdir)
        self.init_appinfomod()

    def init_dirs(self, initdir):
        self.dirs = dict()
        self.reldirs = dict()

        self.dirs['app'] = initdir
        for appdir in appdirs:
            dirname, basedir, dirext = appdir

            if dirname == 'src':
                dirext = 'src.' + ('console', 'gui')[self.gui]
            elif dirname == 'binaries':
                dirext += '.' + ('console', 'gui')[self.gui]
            self.dirs[dirname] = os.path.normpath(
                os.path.join(self.dirs[basedir], dirext))

        for appreldir in appreldirs:
            dirname, basedir, dirext = appreldir
            dirrel = self.dirs[dirext]
            self.reldirs[dirname] = os.path.normpath(
                os.path.relpath(self.dirs[basedir], dirrel))

    def init_appinfomod(self):
        try:
            foundmodule = imp.find_module(appinfomodname,
                                          [self.dirs['src']])
        except Exception, e:
            raise e

        try:
            self.appinfomod = imp.load_module(appinfomodname, *foundmodule)
        except Exception, e:
            raise e

    def getreldir(self, base, rel):
        return os.path.join(base, rel)

    def getdir(self, name):
        return self.dirs[name]

    def get(self, varname):
        varnamelow = varname.lower()
        for attrname in dir(self.appinfomod):
            if varnamelow == attrname.lower():
                return getattr(self.appinfomod, attrname)

        # Not found -> return default value
        return appdefaults[varnamelow]

    def validappid(self):
        try:
            valid_uuid = uuid.UUID(self.get('AppId'), version=4)
        except ValueError:
            value = uuid.uuid4()
            return False, value

        return True, None

    def getappname(self):
        return self.get('AppName')

    def getappexename(self):
        appexename = self.get('AppExeName')
        if sys.platform == 'win32':
            if not appexename.endswith('.exe'):
                appexename += '.exe'
        else:
            if appexename.endswith('.exe'):
                appexename = appexename[:-4]
        return appexename

    def getappconsole(self):
        return self.get('AppConsole')

    def getappscript(self, inspec=False):
        srcdir = self.dirs['src']
        appscript = os.path.normpath(os.path.join(srcdir, 'main.py'))
        if inspec:
            appscript = os.path.normpath(os.path.join('..', appscript))
        if not self.get('AppConsole'):
            appscript += 'w'
        return appscript

    def getapponedir(self):
        return self.get('AppExeType') == 'onedir'

    def getapppyoptimize(self):
        if self.get('AppPyOptimize'):
            return [('O', '', 'OPTION')]
        return []

    def getuacadmin(self, exe_kwargs):
        if self.get('AppUACManifest'):
            exe_kwargs['uac-admin'] = self.get('AppUACAdmin')
            exe_kwargs['uac-uiaccess'] = self.get('AppUACUiAccess')

    def getfilepath(self, dirname, appvar, ext, optional=None):
        filedir = self.dirs[dirname]
        filename = self.get(appvar) + '.' + ext
        filepath = os.path.join(filedir, filename)
        if os.path.isfile(filepath):
            return glob.glob(filepath)[0]
        if optional:
            filename = optional + '.' + ext
            filepath = os.path.join(filedir, filename)
            if os.path.isfile(filepath):
                return glob.glob(filepath)[0]
        return None

    def getspecfile(self):
        ext = ('console', 'gui')[self.gui] + '.spec'
        return self.getfilepath('script', 'AppName', ext, 'pyinstaller')

    def getpyfile(self):
        return self.getfilepath('src', 'AppName', 'pyw', 'main')

    def getpywfile(self):
        return self.getfilepath('src', 'AppName', 'pyw', 'main')

    def getissfile(self):
        return self.getfilepath('script', 'AppName', 'iss', 'innosetup')

    def clean_srcdir_backups(self):
        clean_dir = self.dirs['src']
        for root, dirs, files in os.walk(clean_dir):
            for pyc_pattern in pyc_patterns:
                for filename in fnmatch.filter(files, pyc_pattern):
                    os.remove(os.path.join(root, filename))

    def clean_srcdir_pyc(self):
        clean_dir = self.dirs['src']
        for root, dirs, files in os.walk(clean_dir):
            for clean_pattern in clean_patterns:
                for filename in fnmatch.filter(files, clean_pattern):
                    os.remove(os.path.join(root, filename))

    def compile_srcdir(self):
        compile_dir = self.dirs['src']
        for root, dirs, files in os.walk(compile_dir):
            for compile_pattern in compile_patterns:
                for filename in fnmatch.filter(files, compile_pattern):
                    py_compile.compile(file=os.path.join(root, filename),
                                       doraise=True)

    def zip_exe_dist(self):
        dstdir = self.dirs['zip_dist']
        srcdir = self.dirs['exe_dist']
        if self.getapponedir():
            srcdir = os.path.normpath(os.path.join(srcdir, self.getappname()))

        zipprefix = self.getappname() + '-' + self.get('Appversion')
        dstzipname = zipprefix + '.zip'

        dstzip = zipfile.ZipFile(os.path.join(dstdir, dstzipname), mode='w')

        for root, dirs, files in os.walk(srcdir):
            for f in files:
                arcname = zipprefix + '/' + f
                dstzip.write(os.path.normpath(os.path.join(root, f)),
                             arcname=arcname)

        # Add inifile to make it portable
        arcname = zipprefix + '/' + self.getappname() + '.ini'
        dstzip.writestr(arcname, '')

        dstzip.close()

    def check_dir_build(self):
        return os.path.isdir(self.dirs['build'])

    def make_del_dir(self, dirname):
        dirpath = self.dirs[dirname]
        if os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        os.mkdir(dirpath)

    def make_dirs_zip(self):
        map(self.make_del_dir, ['zip', 'zip_dist'])

    def make_dirs_exe(self):
        map(self.make_del_dir, ['binaries', 'exe', 'exe_build', 'exe_dist'])

    def check_dirs_exe_dist(self):
        distdir = self.dirs['exe_dist']
        return os.path.isdir(distdir) and len(os.listdir(distdir))

    def make_dirs_setup(self):
        map(self.make_del_dir, ['setup', 'setup_build', 'setup_dist'])

    def prepare_issfile(self):
        # Create temp file
        ofilehandle, ofilepath = tempfile.mkstemp()  # open temporary file
        ofile = os.fdopen(ofilehandle, 'w')  # wrap fhandle in "file object"

        ifilepath = self.getissfile()
        ifile = open(ifilepath)  # open original file
        for line in ifile:
            line = self.replace_lines(line)
            ofile.write(line)

        ofile.close()  # close temp file
        ifile.close()  # close original file

        equal = filecmp.cmp(ifilepath, ofilepath, shallow=False)
        if not equal:
            os.remove(ifilepath)  # remove original file
            shutil.move(ofilepath, ifilepath)  # move new file
        else:
            os.remove(ofilepath)  # remove temp file

    def replace_lines(self, line):
        if line.startswith('#define'):
            # Do the replacement magic here
            define, defname, defvalue = line.strip('\r\n').split(None, 2)

            # check if defname is on the list of replacements
            # if yes replace using "" for the value
            # else write the original line
            defkey = defname[2:]  # remove "My"
            # Remove the quotes from the value
            value = defvalue.strip('"')

            if defkey in inno_replace:
                value = self.get(defkey)
            elif defkey in inno_dirs:
                dirname = inno_dirs[defkey]
                value = self.reldirs[dirname]
                if dirname == 'setup_build' and self.getapponedir():
                    value = os.path.join(value, self.getappname())

            line = ' '.join([define, defname, '"%s"' % value]) + '\n'

        return line

    def copy_datas(self):
        basesrc = self.dirs['base']
        basedst = self.dirs['exe_dist']

        if self.getapponedir():
            basedst = os.path.normpath(
                os.path.join(basedst, self.getappname()))

        for reldstdir, items in self.get('copy_datas').iteritems():
            dstdir = os.path.normpath(os.path.join(basedst, reldstdir))
            for item in items:
                srcitems = glob.glob(
                    os.path.normpath(os.path.join(basesrc, item)))
                for srcitem in srcitems:
                    if os.path.isdir(srcitem):
                        shutil.copytree(srcitem, dstdir)
                    else:
                        shutil.copy2(srcitem, dstdir)

    def toc_datas(self, tree_class):
        basesrc = self.dirs['base']
        tocs = list()

        for data in ['toc_datas', 'copy_datas']:
            for reldstdir, items in self.get(data).iteritems():
                dstdir = os.path.normpath(reldstdir)
                for item in items:
                    fullitem = os.path.normpath(os.path.join(basesrc, item))

                    if os.path.isdir(fullitem):
                        tocs += tree_class(fullitem, prefix=dstdir)
                        continue

                    if os.path.isfile(fullitem):
                        dstname = os.path.join(dstdir,
                                               os.path.basename(fullitem))
                        tocs += [(dstname, fullitem, 'DATA')]
                        continue

                    # Asume a glob patten was passed
                    for srcitem in glob.glob(fullitem):
                        if os.path.isdir(srcitem):
                            tocs += tree_class(srcitem, prefix=dstdir)
                        else:  # isfile
                            dstname = os.path.join(dstdir,
                                                   os.path.basename(srcitem))
                            tocs += [(dstname, srcitem, 'DATA')]

        return tocs

    def copy_exedist_to_setupbuild(self):
        src = self.dirs['exe_dist']
        dst = self.dirs['setup_build']

        if self.getapponedir():
            dst = os.path.join(dst, self.getappname())

        src_files_dirs = glob.glob(os.path.join(src, '*'))

        # copy_files
        map(lambda x: shutil.copy(x, dst),
            filter(os.path.isfile, src_files_dirs))

        # copy_dirs
        map(lambda x: shutil.copytree(x, dst),
            filter(os.path.isdir, src_files_dirs))
