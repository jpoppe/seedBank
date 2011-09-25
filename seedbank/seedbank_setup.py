#!/usr/bin/env python

"""

seedBank setup tool

Copyright 2009-2011 Jasper Poppe <jpoppe@ebay.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This tool downloads the needed netboot tarballs from the internet and
extracts the needed files to the right place, it's also able to integrate
the 'non free' firmware files into the Debian netboot initrd.

"""

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2011 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '1.0.0'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'release candidate'

import fnmatch
import optparse
import os
import seedlib
import shutil
import sys
import tarfile

sys.path.append('/etc/seedbank')

from settings import setup_dists, setup_urls, sp_paths


class SetupNetboot(object):
    """manage the netboot system files"""

    def __init__(self):
        self.temp = '/tmp/seedbank'

    def _untar_files(self, archive, files):
        """deletes seedbank temp directory, create directory and untar selected
        files from a gzipped tarball"""
        if not seedlib.rmtree(self.temp):
            return
        elif not seedlib.makedirs(self.temp):
            return

        try:
            os.chdir(self.temp)
            t = tarfile.open(archive, 'r:gz')
            t.extractall('', members=(t.getmember(m) for m in files))
            t.close()
        except IOError:
            print ('error: failed to extract "%s" to "%s"' %
                (archive, self.temp))
        else:
            print ('info: extracted files to "%s"' % (self.temp))
            return True

    def _untar_all(self, archive, destination):
        """extract all files from a gzipped tarball"""
        try:
            t = tarfile.open(archive, 'r:gz')
            t.extractall(destination)
            t.close()
        except IOError:
            print ('error: failed to extract "%s" to "%s"' % (archive,
                destination))
        else:
            print ('info: extracted files to "%s"' % (destination))
            return True

    def _move(self, destination):
        """search and move all files from a given directory"""
        if os.path.isdir(destination):
            print ('info: "%s" already exists, files will be overwritten' %
                destination)
        elif not seedlib.makedirs(destination):
            return

        files = (os.path.join(root, filename) for root, _, files in
            os.walk(self.temp) if files for filename in files)
        for source in files:
            try:
                shutil.copy2(source, destination)
            except IOError:
                print ('error: unable to copy "%s" to "%s"' % (source,
                    destination))
                return
        
        print ('info: moved files to "%s"' % destination)
        seedlib.rmtree(self.temp)
        return True

    def _download(self, source, destination):
        """download a file via wget"""
        sourcefile = os.path.basename(source)
        target = os.path.join(destination, sourcefile)
        command = ['/usr/bin/wget', '--tries=3', '--timeout=15', source, '-P', destination]
        
        if os.path.isfile(target):
            print ('info: "%s" is already in "%s"' % (sourcefile, destination))
            return True
        elif not seedlib.makedirs(destination):
            return

        print ('info: starting download for "%s"' % source)
        print (command)
        result = seedlib.run(command, True)
        if result.retcode:
            print ('error: failed to download "%s"' % source)
            return
        else:
            print ('info: downloaded "%s"' % source)
            return True

    def _extract(self, prefix, files, source, destination, target):
        """extact files to the seedbank temp directory and move those"""
        archive = os.path.join(destination, os.path.basename(source))
        files = (os.path.join(prefix, filename) for filename in files)
        if not self._untar_files(archive, files):
            return
        elif not self._move(target):
            return
        else:
            return True

    def _extract_debs(self, directory):
        """extract files from all debian packages in a directory"""
        os.chdir(directory)
        for file in os.listdir(directory):
            if fnmatch.fnmatch(file, '*.deb'):
                command = ['/usr/bin/dpkg', '-x', file, 'temp']
                result = seedlib.run(command)
                if result.retcode:
                    return
                print ('info: extracted "%s"' % file)
        return True

    def _extract_initrd(self, initrd, temp_initrd):
        """extract an initrd image"""
        os.chdir(temp_initrd)
        result = seedlib.run_pipe('/bin/zcat %s | /bin/cpio -iv' % initrd)
        if not result.retcode:
            print ('info: extracted "%s" to "%s"' % (initrd, temp_initrd))
            return True

    def _create_initrd(self, initrd, temp_initrd):
        """create an initrd image"""
        os.chdir(temp_initrd)
        result = seedlib.run_pipe('find . -print0 | cpio -0 -H newc -ov | '
            'gzip -c > %s' % initrd)
        if not result.retcode:
            print ('info: created "%s" from "%s"' % (initrd, temp_initrd))
            return True

    def _merge_directories(self, source, destination):
        source = os.path.join(source, 'lib/firmware')
        destination = '/tmp/seedbank/initrd/lib/firmware'
        result = seedlib.move(source, destination)
        return result

    def _pxe_default(self):
        """manage the pxelinux.cfg default file"""
        source = os.path.join(sp_paths['templates'], 'pxe-default')
        directory = os.path.join(sp_paths['tftpboot'], 'pxelinux.cfg')
        destination = os.path.join(directory, 'default')

        if os.path.isfile(destination):
            print ('info: default pxelinux.cfg file "%s" found, will not '
            'overwrite' % destination)
            return True
        else:
            print ('info: no default pxelinux.cfg file "%s" found, will '
            'generate' % destination)

        if not os.path.isdir(directory):
            seedlib.makedirs(directory)

        try:
            shutil.copy2(source, destination)
        except IOError:
            print ('error: unable to copy "%s" to "%s"' % (source, destination))
        else:
            return True

    def _disable_usb(self, temp_initrd):
        """remove usb storage support from initrd"""
        for root, _, _ in os.walk(temp_initrd):
            if 'kernel/drivers/usb/storage' in root:
                try:
                    shutil.rmtree(root)
                except IOError:
                    print ('error: unable to copy "%s" to "%s"' % root)
                else:
                    print ('info: usb storage support is now disabled in '
                        'initrd image (fixes "root partition not found" error)')
                    return True
        sys.exit()

    def syslinux(self, destination):
        """download syslinux and extract needed files"""
        files = ('core/pxelinux.0', 'com32/menu/menu.c32',
            'com32/menu/vesamenu.c32')
        prefix = os.path.basename(setup_urls['syslinux']).rstrip('.tar.gz')

        if not self._download(setup_urls['syslinux'], destination):
            return
        elif not self._extract(prefix, files, setup_urls['syslinux'],
            destination, sp_paths['tftpboot']):
            return
        elif not self._pxe_default():
            return
        else:
            return True

    def debian_firmware(self, selection, release):
        """download and integrate the debian non free firmware"""
        destination = os.path.join(sp_paths['archives'], 'firmware-' + release)
        temp_initrd = os.path.join(self.temp, 'initrd')
        temp_firmware = os.path.join(self.temp, 'firmware')
        firmware = os.path.join(destination, 'firmware.tar.gz')
        initrd = os.path.join(sp_paths['tftpboot'], 'seedbank', selection,
            'initrd.gz')
        url = setup_urls['firmware'].replace('${release}', release)

        if not self._download(url, destination):
            print ('error: failed to download "%s"' % url)
            return
        elif not self._untar_all(firmware, temp_firmware):
            print ('error: failed to extract "%s"' % firmware)
            return
        elif not self._extract_debs(temp_firmware):
            print ('error: failed to extract debs in "%s"' % temp_firmware)
            return
        elif not seedlib.makedirs(temp_initrd):
            print ('error: failed to create directory "%s"' % temp_initrd)
            return
        elif not self._extract_initrd(initrd, temp_initrd):
            print ('error: failed to extract "%s"' % temp_initrd)
            return
        elif not self._merge_directories(os.path.join(temp_firmware, 'temp'),
            temp_initrd):
            print ('error: failed to merge firmware files into initrd')
            return
        elif not self._disable_usb(temp_initrd):
            print ('error: failed to disable USB bug in "%s"' % temp_initrd)
            return
        elif not self._create_initrd(initrd, temp_initrd):
            print ('error: failed to build initrd "%s"' % initrd)
            return
        else:
            seedlib.rmtree(self.temp)
            return True

    def netboot(self, selection, dist, release, arch):
        """download a netboot tarball"""
        source = '%s/%s/dists/%s/main/installer-%s/current/images/netboot/' \
        'netboot.tar.gz' % (setup_urls[dist], dist, release, arch)
        destination = os.path.join(sp_paths['archives'], selection)
        prefix = os.path.join('./%s-installer' % dist, arch)
        files = ('initrd.gz', 'linux')
        target = os.path.join(sp_paths['tftpboot'], 'seedbank', selection)

        if not self._download(source, destination):
            return
        elif not self._extract(prefix, files, source, destination, target):
            return
        else:
            return True


def list_releases():
    """list alll avaliable releases"""
    for dist in setup_dists['releases']:
        print (dist)

def main():
    """the main application"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    for path in sp_paths:
        if not sp_paths[path].startswith('/'):
            sp_paths[path] = os.path.join(base_dir, sp_paths[path])

    parser = optparse.OptionParser(prog='seedbank_setup', version=__version__)

    parser.set_description('seedBank setup - (c) 2009-2011 Jasper Poppe '
    '<jpoppe@ebay.com>')

    parser.set_usage('%prog [-h|-l|-i|-s] | [-r] <release>')

    parser.add_option('-l', '--list', dest='list', help='list available releases',
        action='store_true')

    parser.add_option('-s', '--syslinux', dest='syslinux', help='download and install '
        'syslinux pxe files', action='store_true')

    parser.add_option('-i', '--installed', dest='installed', help='list installed releases',
        action='store_true')

    parser.add_option('-r', '--remove', dest='remove', help='remove an installed release',
        action='store_true')

    (opts, args) = parser.parse_args()

    if not os.geteuid() == 0:
        parser.error('only root can run this script')

    install = SetupNetboot()

    if opts.list:
        list_releases()
    elif opts.installed:
        list = seedlib.FormatListDir('releases')
        list.listdir(os.path.join(sp_paths['tftpboot'], 'seedbank'), 'dirs')
        list.show()
    elif opts.syslinux:
        install.syslinux(os.path.join(sp_paths['archives'], 'syslinux'))
    elif not args:
        parser.print_help()
        sys.exit(0)
    elif len(args) != 1:
        parser.error('specify a release eg.: debian-lenny-amd64 (use -l to '
        'list available releases)')
    elif opts.remove:
        if not args[0]:
            parser.error('no distro specified')
        distro = os.path.join(sp_paths['tftpboot'], 'seedbank', args[0])
        if not os.path.isdir(distro):
            parser.error('distro "%s" not found')
        seedlib.rmtree(distro)
        seedlib.rmtree(os.path.join(sp_paths['archives'], args[0]))
        release = args[0].split('-')[1]
        firmware = os.path.join(sp_paths['archives'], 'firmware-' + release)
        if os.path.isdir(firmware):
            seedlib.rmtree(firmware)
    else:
        selection = args[0]
        if not selection in setup_dists['releases']:
            parser.error('"%s" is an unknown release (use -l to list available '
                'releases)' % (selection))
        else:
            try:
                dist, release, arch = selection.split('-')
            except ValueError:
                parser.error('"%s" is a known but invalid release (check '
                    'settings.py)' % (selection))

        if not install.netboot(selection, dist, release, arch):
            return

        if selection in setup_dists['firmwares']:
            install.debian_firmware(selection, release)

if __name__ == '__main__':
    main()
