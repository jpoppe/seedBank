#!/usr/bin/env python

# Copyright 2009-2012 Jasper Poppe <jpoppe@ebay.com>
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

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '2.0.0rc3'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import os
import re
import urllib
import logging
import yaml

import settings
import utils

# globals
cfg = settings.parse_cfg()


class GeneratePxe:
    """manage and generate pxe files"""
    
    def __init__(self, args):
        """set arguments as class variables"""
        self.seeds = args.seeds
        self.fqdn = args.fqdn
        self.host_name, self.dns_domain = utils.fqdn_split(args.fqdn)
        self.variables = args.variables
        self.config = args.config
        self.overlay = args.overlay
        self.address = args.address
        self.release = args.release
        self.puppet = args.puppet
        self.pxe_variables = {}

    def state_remove(self):
        """if there are one or more state files starting with the fqdn, remove
        those"""
        prefix = self.fqdn + '_'
        for file_name in os.listdir(cfg['paths']['status']):
            if file_name.startswith(prefix) and file_name.endswith('.state'):
                target = os.path.join(cfg['paths']['status'], file_name)
                utils.file_delete(target)

    def generate(self):
        """generate the pxe boot file"""
        self.pxe_variables.update({
            'config': self.config,
            'seeds': self.seeds,
            'seed_host': cfg['settings']['seed_host'],
            'seed_port': cfg['settings']['bottle_port'],
            'address': self.address,
            'overlay': self.overlay,
            'puppet_manifests': self.puppet,
            'host_name': self.host_name,
            'dns_domain': self.dns_domain,
            'fqdn': self.fqdn,
            'query': urllib.urlencode([('address', self.address)]),
            'date_generated': utils.date_time(),
            'date_disabled': '',
            'kernel': '%s/%s/%s' % ('seedbank', self.release, 'linux'),
            'initrd': '%s/%s/%s' % ('seedbank', self.release, 'initrd.gz')
        })

        if self.config:
            yaml_file = os.path.join(cfg['paths']['configs'], self.config)
            yaml_file = yaml_file + '.yaml'
            overrides = utils.yaml_read(yaml_file)
            if 'pxe' in overrides:
                cfg['pxe'].update(overrides['pxe'])
        values = cfg['pxe']
        self.pxe_variables.update(values)

        distribution = self.release.split('-')[0]
        file_name = cfg['templates']['pxe_' + distribution]
        file_name = os.path.join(cfg['paths']['templates'], file_name)
        if not os.path.isfile(file_name):
            logging.error('file "%s" does not exist (hint: check the templates '
                'section in your settings)', file_name)
            raise utils.FatalException()

        pxe_variables_custom = []
        for variable in self.variables:
            key, value = variable
            pxe_variables_custom.append('# %s = %s' % (key, value))
            self.pxe_variables[key] = value
        pxe_variables_custom = '\n'.join(pxe_variables_custom)

        data = utils.file_read(file_name)
        data = utils.apply_template(data, self.pxe_variables, file_name)
        if pxe_variables_custom:
            data = re.sub(
                '(#\n# \*\*\* end - seedBank pxe variables \*\*\*)',
                pxe_variables_custom + '\n\\1', data)
        return data

    def write(self, contents):
        """write the pxe boot file"""
        file_name = os.path.join(cfg['paths']['tftpboot'], 'pxelinux.cfg',
            self.address)
        directory = os.path.dirname(file_name)
        utils.make_dirs(directory)
        utils.file_delete('%s.disabled' % file_name)
        utils.file_write(file_name, contents)

    def hook_enable(self):
        """apply PXE variables on the configured enable hook(s) and run the
        hook(s)"""
        for hook in cfg['hooks']['enable']:
            hook = utils.apply_template(hook, self.pxe_variables)
            logging.info('found enable hook "%s"', hook)
            utils.run(hook)


class ExternalNodes(object):
    """use external nodes for getting configuration details"""
    
    def __init__(self, provider, values):
        """initialize variables"""
        self.provider = provider
        self.values = values

    def _gather_http(self):
        """get internal nodes information via http ot https, delete the first line"""
        url = utils.apply_template(self.provider, self.values)
        result = utils.read_url(url)
        if result:
            del result[0]
        result = ''.join(result)
        return self._return(yaml.load(result))

    def _return(self, result):
        if result:
            return dict([('external_' + k, v) for k, v in result.items()])
        else:
            print ('warning: no external node information found')

    def _gather_script(self):
        """get node information via a lookup script"""
        command = utils.apply_template(self.provider, self.values)
        command = command.split(' ')
        result = utils.run(command)
        if not result.retcode:
            return self._return(yaml.load(result.output))

    def gather(self):
        """get the type of the external nodes data provider and gather data"""
        if self.provider.startswith('http://') or self.provider.startswith('https://'):
            return self._gather_http()
        elif not self.provider:
            return self._gather_http()
        else:
            return self._gather_script()
