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


import os


class ListResources:
    """this class lists the available seedBank resources and prints to stdout"""

    def __init__(self, cfg):
        """initialize class variables"""
        self.lists = []
        self.cfg = cfg

    def _list_files(self, path, ext=None):
        """list files in a path and strip ext from the file name"""
        files = {}
        if not os.path.isdir(path):
            return files

        for item in os.listdir(path):
            name = os.path.join(path, item)
            if os.path.isfile(name):
                if ext and item.endswith(ext):
                    files[os.path.splitext(item)[0]] = name
                else:
                    files[item] = name
        return files

    def _list_dirs(self, path):
        """"list directories"""
        dirs = {}
        if not os.path.isdir(path):
            return dirs

        for item in os.listdir(path):
            name = os.path.join(path, item)
            if os.path.isdir(name):
                dirs[item] = name
        return dirs

    def _add(self, category, header):
        """add a category to the result list"""
        category.insert(0, header + ':')
        self.lists.append(category)

    def _format_available(self, configured, installed):
        """prefix available isos and netboot images with an * and append the
        path"""
        result = []
        for item in configured:
            if item in installed:
                result.append('*%s -> %s' %(item, installed[item]))
            else:
                result.append(item)
        result.sort()
        return result
    
    def configs(self):
        """list available configuration overrides"""
        items = self._list_files(self.cfg['paths']['configs'], '.yaml')
        self._add(items.keys(), 'config overrides')

    def netboots(self):
        """list local available and configured netboot images"""
        path = os.path.join(self.cfg['paths']['tftpboot'], 'seedbank')
        installed = self._list_dirs(path)
        configured = self.cfg['distributions']['netboots']
        images = self._format_available(configured, installed)
        self._add(images, 'netboot images')

    def isos(self):
        """list local available and configured isos"""
        installed = self._list_files(self.cfg['paths']['isos'], '.iso')
        configured = self.cfg['distributions']['isos']
        images = self._format_available(configured, installed)
        self._add(images, 'ISOs')

    def puppet(self):
        """list available Puppet manifests"""
        items = self._list_files(self.cfg['paths']['puppet_manifests'], '.pp')
        self._add(items.keys(), 'Puppet manifests')

    def overlays(self):
        """list available file overlays"""
        items = self._list_dirs(self.cfg['paths']['overlays'])
        self._add(items.keys(), 'file overlays')

    def seeds(self):
        """list available preseed files"""
        items = self._list_files(self.cfg['paths']['seeds'], '.seed')
        self._add(items.keys(), 'seeds')

    def pxe(self):
        """list available pxe linux configurations"""
        path = os.path.join(self.cfg['paths']['tftpboot'], 'pxelinux.cfg')
        items = self._list_files(path)
        items = [os.path.join(path, item) for item in items]
        self._add(items, 'pxelinux configurations')

    def print_list(self):
        """print all selected lists, last list to be printed will not add an
        empty line at the end"""
        if len(self.lists) == 1:
            print ('\n'.join(self.lists[0]))
        elif len(self.lists) > 1:
            for item in self.lists[:-1]:
                print ('\n'.join(item))
                print('')
            print ('\n'.join(self.lists[-1]))
