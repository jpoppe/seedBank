#!/usr/bin/env python

# Copyright 2009-2012 Jasper Poppe <jgpoppe@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'Jasper Poppe <jgpoppe@gmail.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '2.0.0rc6'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jgpoppe@gmail.com'
__status__ = 'production'

import fnmatch
import logging
import os

import utils


class Manage:
    """manage netboot images, ISO, syslinux and permissions files"""

    def __init__(self, cfg):
        """initialize class variables"""
        self.cfg = cfg
        self.temp = os.path.join(self.cfg['paths']['temp'], 'seedbank')

    def _move(self, dst):
        """search and move all files from a given directory"""
        utils.make_dirs(dst)
        files = (os.path.join(root, file_name) for root, _, files in
            os.walk(self.temp) if files for file_name in files)
        for src in files:
            utils.file_copy(src, dst)

    def _download(self, src, dst_path):
        """download a file"""
        src_file = os.path.basename(src)
        dst = os.path.join(dst_path, src_file)
        if os.path.isfile(dst):
            logging.info('"%s" already exists, download skipped', dst)
            return
        utils.make_dirs(dst_path)
        utils.download(src, dst)

    def _extract(self, prefix, files, src, dst, target):
        """extract files to the seedbank temp directory and move those"""
        archive = os.path.join(dst, os.path.basename(src))
        files = (os.path.join(prefix, file_name) for file_name in files)
        temp = os.path.join(self.temp, 'manage')
        if os.path.isdir(temp):
            utils.rmtree(temp)
        utils.make_dirs(temp)
        #print(prefix, files, src, dst, name)
        print target
        utils.untar_files(archive, files, temp)
        return
        self._move(target)
        utils.rmtree(temp)

    def _extract_debs(self, directory):
        """extract files from all debian packages in a directory"""
        os.chdir(directory)
        for file_name in os.listdir(directory):
            if fnmatch.fnmatch(file_name, '*.deb'):
                result = utils.call(['dpkg', '-x', file_name, 'temp'])
                if result:
                    err = 'failed to extract package "%s"' % file_name
                    raise utils.FatalException(err)
                logging.info('extracted "%s"', file_name)

    def _pxe_default(self):
        """manage the pxelinux.cfg default file"""
        src = os.path.join(self.cfg['paths']['templates'], 'pxe_default')
        directory = os.path.join(self.cfg['paths']['tftpboot'], 'pxelinux.cfg')
        dst = os.path.join(directory, 'default')
        if os.path.isfile(dst):
            return
        logging.info('created default pxelinux.cfg file "%s"', dst)
        utils.make_dirs(directory)
        utils.file_copy(src, dst)

    def _disable_usb(self, temp_initrd):
        """remove usb storage support from initrd"""
        for root, _, _ in os.walk(temp_initrd):
            if 'kernel/drivers/usb/storage' in root:
                if utils.rmtree(root):
                    logging.info('usb storage support has been disabled in the '
                        'initrd image (fixes "root partition not found" error)')

    def _debian_firmware(self, target):
        """download and integrate the debian non free firmware"""
        distribution, release, _ = target.split('-')
        path = 'firmware-' + distribution + '-' + release
        dst = os.path.join(self.cfg['paths']['archives'], path)
        temp_initrd = os.path.join(self.temp, 'initrd')
        temp_firmware = os.path.join(self.temp, 'firmware')
        firmware = os.path.join(dst, 'firmware.tar.gz')
        initrd = os.path.join(self.cfg['paths']['tftpboot'], 'seedbank', target,
            'initrd.gz')
        url = self.cfg['urls']['debian_firmware'].replace('${release}', release)
        self._download(url, dst)
        utils.untar(firmware, temp_firmware)
        self._extract_debs(temp_firmware)
        utils.make_dirs(temp_initrd)
        utils.initrd_extract(temp_initrd, initrd)
        src = os.path.join(temp_firmware, 'temp', 'lib/firmware')
        dst = os.path.join(self.temp, 'initrd/lib/firmware')
        utils.file_move(src, dst)
        self._disable_usb(temp_initrd)
        utils.initrd_create(temp_initrd, initrd)

    def syslinux(self):
        """download syslinux and extract required files"""
        dst = os.path.join(self.cfg['paths']['archives'], 'syslinux')
        files = ('core/pxelinux.0', 'com32/menu/menu.c32',
            'com32/menu/vesamenu.c32')
        prefix = os.path.basename(self.cfg['urls']['syslinux'])
        prefix = prefix.rstrip('.tar.gz')
        self._download(self.cfg['urls']['syslinux'], dst)
        self._extract(prefix, files, self.cfg['urls']['syslinux'], dst,
            self.cfg['paths']['tftpboot'])
        self._pxe_default()

    def iso_debian(self, name):
        """download a Debian ISO"""
        distribution, release, architecture, flavour = name.split('-')
        if flavour == 'mini':
            url = self.cfg['urls'][distribution]
            url = os.path.join(url, 'debian/dists', release, 'main/installer-' +
                architecture, 'current/images/netboot/mini.iso')
        else:
            if release == self.cfg['distributions']['debian_iso_current']:
                release = 'current'
            url = self.cfg['urls'][distribution + '_iso']
            url = os.path.join(url, release, architecture, 'iso-cd')
            data = utils.scrape_tag(url, 'a')
            isos = [link for link in data if link.endswith('.iso')]
            iso_split = isos[0].split('-')
            version = iso_split[1]
            iso_file = '-'.join(('debian', version, architecture, flavour))
            iso_file = iso_file + '.iso'
            url = os.path.join(url, iso_file)
        return url

    def iso_ubuntu(self, name):
        """download an Ubuntu ISO, the mini ISO comes from a different source
        then the others, it will also detect and choose the current beta or
        alpha release when there is no stable release"""
        distribution, release, architecture, flavour = name.split('-')
        if flavour == 'mini':
            url = self.cfg['urls'][distribution]
            url = os.path.join(url, 'ubuntu/dists', release, 'main/installer-' +
                architecture, 'current/images/netboot/mini.iso')
        else:
            url = self.cfg['urls'][distribution + '_iso']
            url = os.path.join(url, release)
            data = utils.scrape_tag(url, 'a')
            isos = [link for link in data if link.endswith('.iso')]
            iso_split = isos[0].split('-')
            version = iso_split[1]
            if len(iso_split) == 4:
                iso_file = '-'.join((distribution, version, flavour,
                    architecture))
            elif len(iso_split) == 5:
                state = iso_split[2]
                iso_file = '-'.join((distribution, version, state, flavour,
                    architecture))
                logging.warning('no stable release found for "%s"', name)
            iso_file = iso_file + '.iso'
            url = os.path.join(url, iso_file)
        return url
     
    def iso(self, name):
        """download ISOs"""
        dst = os.path.join(self.cfg['paths']['isos'], name + '.iso')
        if os.path.isfile(dst):
            logging.info('nothing to do, "%s" already exists', dst)
            return
        distribution = name.split('-', 1)[0]
        if distribution == 'ubuntu':
            url = self.iso_ubuntu(name)
        elif distribution == 'debian':
            url = self.iso_debian(name)
        utils.make_dirs(self.cfg['paths']['isos'])
        utils.download(url, dst)

    def netboot(self, name):
        """download, extract and patch netboot images"""
        distribution, release, architecture = name.split('-')
        src = '%s/%s/dists/%s/main/installer-%s/current/images/netboot/'\
            'netboot.tar.gz' % (self.cfg[distribution]['url_main'], distribution,
            release, architecture)
        dst = os.path.join(self.cfg['paths']['archives'], name)
        prefix = os.path.join('./%s-installer' % distribution, architecture)
        files = ('initrd.gz', 'linux')
        name = os.path.join(self.cfg['paths']['tftpboot'], 'seedbank', name)
        self._download(src, dst)
        self._extract(prefix, files, src, dst, name)
        firmware = distribution + '-' + release
        if firmware in self.cfg['distributions']['firmwares']:
            self._debian_firmware(name)

    def _remove_netboot(self, name):
        """remove a netboot image and if defined the related firmware files"""
        path = os.path.join(self.cfg['paths']['tftpboot'], 'seedbank', name)
        if not utils.rmtree(path):
            logging.info('release "%s" has not been installed', name)
        else:
            utils.rmtree(os.path.join(self.cfg['paths']['archives'], name))
        release = name.split('-')[1]
        firmware = os.path.join(self.cfg['paths']['archives'],
            'firmware-' + release)
        if not utils.rmtree(firmware):
            logging.info('firmware "%s" not found, nothing to do', firmware)

    def _remove_iso(self, name):
        """remove an installation ISO"""
        file_name = os.path.join(self.cfg['paths']['isos'], name + '.iso')
        if not utils.file_delete(file_name):
            logging.info('release "%s" has not been installed', name)

    def remove(self, name):
        """remove a release"""
        if name in self.cfg['distributions']['netboots']:
            self._remove_netboot(name)
        elif name in self.cfg['distributions']['isos']:
            self._remove_iso(name)
        else:
            logging.error('release "%s" has not been defined in settings', name)
