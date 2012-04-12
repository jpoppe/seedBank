"""this module processes the configuration"""

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

import ast
import logging
import os
import re

import utils


def parse_cfg():
    """validate the configuration"""
    settings = None
    override_files = ['./settings.yaml', '~/.seedbank/settings.yaml']
    settings_file_name = '/etc/seedbank/settings.yaml'
    files = override_files + [settings_file_name]

    for file_name in files:
        if os.path.isfile(file_name):
            settings_file = file_name
            break

    settings = utils.yaml_read(settings_file)
    if not settings:
        err = 'can not find a settings.yaml file (%s)' % ', '.join(files)
        raise utils.FatalException(err)

    path = settings['settings']['configuration_path']
    if not os.path.isdir(path):
        raise utils.FatalException('directory "%s" does not exist' % path)

    if settings_file in override_files:
        logging.info('found settings file "%s", will use this settings file '
            'instead of the default (%s)', settings_file, settings_file_name)

    files = os.listdir(path)
    files = [file_name for file_name in files if file_name.endswith('.yaml')]
    files = [os.path.join(path, file_name) for file_name in files]
    cfg = utils.yaml_read(files)
    cfg.update(settings)

    netboots = []
    for release in cfg['distributions']['netboots']:
        for architecture in cfg['distributions']['architectures']:
            netboots.append(release + '-' + architecture)
    cfg['distributions']['netboots'] = netboots

    isos_version = []
    for iso in cfg['distributions']['isos']:
        distribution, release, version = iso.split('-')
        for architecture in cfg['distributions']['architectures']:
            isos_version.append('%s-%s-%s-%s' % (distribution, release,
                architecture, version))
    cfg['distributions']['isos'] = isos_version

    return cfg

def merge_cfg(config):
    """merge the default configuration with the configuration overrides"""
    cfg = parse_cfg()
    if config:
        yaml_file = os.path.join(cfg['paths']['configs'], config)
        yaml_file += '.yaml'
        overrides = utils.yaml_read(yaml_file)
        for key in cfg:
            if key in overrides:
                cfg[key].update(overrides[key])
    return cfg

def template(fqdn, overlay, config, variables):
    """prepare a dictionary with all template variables"""
    host_name, dns_domain = utils.fqdn_split(fqdn)
    values = {
        'host_name': host_name,
        'dns_domain': dns_domain,
        'fqdn': fqdn
    }
    cfg = merge_cfg(config)
    cfg['seed'].update(values)
    cfg['seed'].update(dict(variables))
    return cfg

    #FIXME: reimplemnt this code
    '''
    missing = []
    for path in cfg['paths'].values():
        if not os.path.isdir(path):
            missing.append(path)

    if missing:
        if len(missing) == 1:
            print ('error: the following configured directory is missing, '
                'please create this directory or change the configuration')
        else:
            print ('error: the following configured directories are missing, '
                'please create those directories or change the configuration')
        print (', '.join(missing))
        sys.exit(1)

        if not len(release.split('-')) == 3:
            error_fatal('"%s" is a malformatted release name, please '
                'correct this in the settings file in the releases section '
                'a valid release should be formatted like: '
                'distribution-release-architecture, for example: '
                'debian-squeeze-amd64'
                % release)
    '''

def override(args, overrides):
    """override optional arguments with arguments from the config file"""
    positionals = ('fqdn', 'release', 'output')
    args_dict = vars(args)
    for key, value in overrides['args'].items():
        if key in positionals:
            logging.warning('positional arguments can not be overriden please '
                'remove "%s" from config "%s"', key, args.config)
        else:
            if type(args_dict[key]) == list:
                value = args_dict[key] + value
            else:
                logging.warning('option "%s" has been defined on the command '
                    'line and in the config override, will use value "%s" from '
                    'the config override "%s"', key, value, args.config)
            setattr(args, key, value)
    return args

def pxe_variables(cfg, address):
    """try to read the pxe variables from the pxelinux.cfg file"""
    file_name = os.path.join(cfg['paths']['tftpboot'], 'pxelinux.cfg', address)
    if not os.path.isfile(file_name):
        raise Exception('"%s" does not exist' % file_name)

    data = utils.file_read(file_name)
    data = re.search(
        r'# \*\*\* start - seedBank pxe variables \*\*\*$(.*?)\*\*\*',
        data, re.M|re.S)
    data = data.group(1).strip()
    data = re.sub('(?m)^#', '', data)
    data = [line.strip() for line in data.split('\n') if line]
    data = [line.split(' =', 1) for line in data]
    data = [(line[0].strip(), line[1].strip()) for line in data]

    lines = []
    values = ['None', 'False', 'True']
    for line in data:
        if line[1].startswith('[') or line[1] in values:
            lines.append((line[0], ast.literal_eval(line[1])))
        else:
            lines.append(line)
    result = dict(lines)
    return result
