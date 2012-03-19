"""this module processes the preseed templates and file overlays """

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

import logging
import os

import utils


def commands_merge(cmds, values):
    """join the commands and apply template pxe variables"""
    cmds = commands_template(cmds, values)
    cmds = '; '.join(cmds)
    return cmds

def commands_template(cmds, values):
    """apply values to a command template"""
    cmds = [utils.apply_template(cmd, values, cmd) for cmd in cmds]
    return cmds


class SeedPimp:
    """collect the seeds and generate the seed file"""

    def __init__(self, cfg, target):
        """initialize the class variables, reload the configuration every time
        this class will be loaded, this is useful when configuration gets
        changed and seedbank is running in daemon mode
        """
        self.cfg = cfg
        self.target = target

    def _merge_seeds(self, seeds, values):
        """merge the main seed file with the recipe(s) and additional seeds 
        return it as a string"""
        result = ''
        for seed in seeds:
            file_name = os.path.join(self.cfg['paths']['seeds'], seed + '.seed')
            data = utils.file_read(file_name)
            result += utils.apply_template(data, values, file_name)
        return result

    def pimp(self, seeds, overlay, manifests):
        """pimp the seed file template"""
        commands = self.cfg['commands']
        if self.target == 'iso':
            cmd_overlay = commands['iso_overlay']
            cmd_late = commands['iso_late_command']
        elif self.target == 'net':
            cmd_overlay = commands['net_overlay']
            cmd_puppet_manifest = commands['net_puppet_manifest']
            cmd_late = commands['net_late_command']

        values = self.cfg['seed']
        if overlay:
            values['late_command'] += cmd_overlay
        if self.target == 'net' and manifests:
            values['late_command'] += commands['net_puppet_manifests']
        for manifest in manifests:
            values['manifest'] = manifest
            if self.target == 'net':
                puppet_command = commands_merge(cmd_puppet_manifest, values)
                values['late_command'] += [puppet_command]
            elif self.target == 'iso':
                src = os.path.join(self.cfg['paths']['templates'],
                self.cfg['templates']['puppet_manifest'])
                path = os.path.join(self.cfg['paths']['temp'], 'seedbank',
                    values['fqdn'], 'iso/iso/seedbank/etc/runonce.d')
                utils.make_dirs(path)
                dst = os.path.join(path, 'puppet_manifest_%s.enabled' %
                    manifest)
                utils.write_template(values, src, dst)
        
        values['late_command'] += cmd_late
        values['early_command'] = commands_merge(values['early_command'],
            values)
        values['late_command'] = commands_merge(values['late_command'], values)

        seed_file = self._merge_seeds(seeds, values)
        logging.debug(seed_file)
        logging.info('%(fqdn)s - generated preseed file', values)
        return seed_file


class Overlay:
    """copy the file overlay directory"""

    def __init__(self, cfg, overlay, fqdn):
        """set the configuration variable, source and destination paths"""
        self.cfg = cfg
        self.dst = os.path.join(self.cfg['paths']['temp'], 'seedbank', fqdn,
            'overlay')
        self.path = os.path.join(self.cfg['paths']['overlays'], overlay)
        if not os.path.isdir(self.path):
            logging.error('overlay directory "%s" does not exist', self.path)
            raise utils.FatalException()

    def prepare(self, values):
        """ apply templates to all the .sb_template files and build the
        fix_perms.sh script from the permissions file"""
        utils.rmtree(self.dst)
        utils.copy_tree(self.path, self.dst)
        for root, _, files in os.walk(self.dst):
            for file_name in files:
                if file_name.endswith('.sb_template'):
                    file_name = os.path.join(root, file_name)
                    utils.write_template(values, file_name)
                    utils.file_move(file_name, os.path.splitext(file_name)[0])


class OverlayPermissions:
    """create and process the overlay permissons script"""

    def __init__(self, cfg):
        """set the configuration variable"""
        self.cfg = cfg

    def generate(self, path):
        """generate an overlay permissions file"""
        perm_file = path + '.permissions'

        overlay_contents = []
        for root, dirs, files in os.walk(path):
            for sub_dir in dirs:
                overlay_contents.append(os.path.join(root, sub_dir))
            for file_name in files:
                if not file_name == '.gitignore':
                    overlay_contents.append(os.path.join(root, file_name))

        perm_list = {}
        for entry in overlay_contents:
            stat = os.stat(entry)
            mode = int(oct(stat.st_mode)[3:])
            entry = entry.split(path, 1)[1]
            if entry == '/root':
                perm_list[entry] = ('0700', 0, 0)
            elif entry.endswith('.ssh'):
                perm_list[entry] = ('0700', 0, 0)
            elif entry.endswith('authorized_keys'):
                perm_list[entry] = ('0700', 0, 0)
            elif entry.startswith('/usr/local/bin'):
                perm_list[entry] = ('0755', 0, 0)
            elif entry == '/etc/rc.local':
                perm_list[entry] = ('0755', 0, 0)
            else:
                perm_list[entry] = ('%04d' % mode, 0, 0)

        if os.path.isfile(perm_file):
            data = utils.file_read(perm_file).split('\n')
            defined_list = {}
            for line in data:
                try:
                    mode, uid, gid, real_path = line.split('\t')
                except ValueError:
                    pass
                else:
                    defined_list[real_path] = (mode, uid, gid)
            for real_path in perm_list:
                if real_path in defined_list:
                    perm_list[real_path] = defined_list[real_path]
       
        data = [] 
        header_file = os.path.join(self.cfg['paths']['templates'],
            self.cfg['templates']['permission_script'])
        header = utils.file_read(header_file)
        data.append(header.strip())
        for key, value in perm_list.items():
            data.append('%s\t%s\t%s\t%s' % (value[0], value[1], value[2], key))
        utils.file_write(perm_file, '\n'.join(data) + '\n')

    def generate_all(self):
        """generate overlay permissions file for all overlays"""
        path = self.cfg['paths']['overlays']
        for overlay in utils.dir_list(path):
            overlay = os.path.join(path, overlay)
            self.generate(overlay)

    def script(self, dst, overlay, prefix):
        """generate the permissions script which will be applied before the end
        of an installation"""
        path = os.path.join(self.cfg['paths']['overlays'], overlay)
        perm_file = path + '.permissions'
        perm_script = os.path.join(dst, 'fix_perms.sh')
        if os.path.isfile(perm_file):
            data = utils.file_read(perm_file).strip()
            lines = data.split('\n')
            lines = [line for line in lines if not line.startswith('#')]
            script = []
            for line in lines:
                try:
                    mode, uid, gid, real_path = line.split('\t')
                except ValueError:
                    logging.error('%s is corrupt, delete or regenerate it with '
                        'the "seedbank manage --overlay" command, or fix the '
                        'file manually, line "%s" contains errors', perm_file,
                        line)
                    raise utils.FatalException()
                else:
                    if prefix:
                        real_path = os.path.join(prefix, real_path[1:])
                        if real_path.endswith('.sb_template'):
                            real_path = os.path.splitext(real_path)[0]
                    script.append('chown %s:%s %s' % (uid, gid, real_path))
                    script.append('chmod %s %s' % (mode, real_path))
            utils.file_write(perm_script, '\n'.join(script))
        else:
            logging.warning('overlay "%s" has been selected but permission '
                'file "%s" does not exist, so all files will be owned by root '
                'and will keep the current permissons which could lead to '
                'problems', overlay, perm_file)
            utils.file_write(perm_script, '')
