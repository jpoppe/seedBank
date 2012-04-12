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

    def __init__(self, cfg):
        self.lists = []
        self.cfg = cfg

    def _list_files(self, path, strip=False):
        if os.path.isdir(path):
            files = [item for item in os.listdir(path)
                if os.path.isfile(os.path.join(path, item))]
            if strip:
                files = [os.path.splitext(file_name)[0] for file_name in files
                    if file_name.endswith(strip)]
            return files
        else:
            return []

    def _list_dirs(self, path):
        if os.path.isdir(path):
            dirs = [item for item in os.listdir(path)
                if os.path.isdir(os.path.join(path, item))]
            return dirs
        else:
            return []

    def _add(self, category, header):
        category.insert(0, header + ':')
        self.lists.append(category)

    def _prefix_installed(self, configured, installed):
        result = []
        for item in configured:
            if item in installed:
                result.append('*' + item)
            else:
                result.append(item)
        result.sort()
        return result
    
    def configs(self):
        items = self._list_files(self.cfg['paths']['configs'], '.yaml')
        self._add(items, 'config overrides')

    def netboots(self):
        path = os.path.join(self.cfg['paths']['tftpboot'], 'seedbank')
        installed = self._list_dirs(path)
        configured = self.cfg['distributions']['netboots']
        images = self._prefix_installed(configured, installed)
        self._add(images, 'netboot images')

    def isos(self):
        installed = self._list_files(self.cfg['paths']['isos'], '.iso')
        configured = self.cfg['distributions']['isos']
        images = self._prefix_installed(configured, installed)
        self._add(images, 'ISOs')

    def puppet(self):
        items = self._list_files(self.cfg['paths']['puppet_manifests'], '.pp')
        self._add(items, 'Puppet manifests')

    def overlays(self):
        items = self._list_dirs(self.cfg['paths']['overlays'])
        self._add(items, 'file overlays')

    def seeds(self):
        items = self._list_files(self.cfg['paths']['seeds'], '.seed')
        self._add(items, 'seeds')

    def pxe(self):
        path = os.path.join(self.cfg['paths']['tftpboot'], 'pxelinux.cfg')
        items = self._list_files(path)
        items = [os.path.join(path, item) for item in items]
        self._add(items, 'pxelinux configurations')

    def print_list(self):
        """print all selected lists, the last list to be printed will not add an
        empty line at the end"""
        if len(self.lists) == 1:
            print ('\n'.join(self.lists[0]))
        elif len(self.lists) > 1:
            for item in self.lists[:-1]:
                print ('\n'.join(item))
                print('')
            print ('\n'.join(self.lists[-1]))
        #else:
        #    print (parser.print_help())
