"""this module processes the arguments"""

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
__version__ = '2.0.0rc5'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import logging
import os
import re

#import daemon
import iso
import net
import manage
import reslist
import rest
import settings
import pimp

import utils


class ParseArguments:
    """process the given arguments"""

    def __init__(self, cfg):
        """load the configuration"""
        self.cfg = cfg

    def list(self, args):
        """list resources based on selected arguments"""
        list_resource = reslist.ListResources(self.cfg)

        if args.all:
            args.netboots = True
            args.seeds = True
            args.overlays = True
            args.configs = True
            args.isos = True
            args.puppet = True
            args.pxe = True

        if args.netboots:
            list_resource.netboots()
        if args.seeds:
            list_resource.seeds()
        if args.overlays:
            list_resource.overlays()
        if args.configs:
            list_resource.configs()
        if args.isos:
            list_resource.isos()
        if args.puppet:
            list_resource.puppet()
        if args.pxe:
            list_resource.pxe()

        list_resource.print_list()

    def _shared(self, args, release):
        """process shared arguments between the net and iso commands"""
        if args.config:
            yaml_file = os.path.join(self.cfg['paths']['configs'], args.config)
            yaml_file += '.yaml'
            overrides = utils.yaml_read(yaml_file)
            if 'args' in overrides:
                args = settings.override(args, overrides)
            config = dict(self.cfg.items() + overrides.items())
        else:
            config = self.cfg

        if args.overlay:
            path = os.path.join(self.cfg['paths']['overlays'], args.overlay)
            if os.path.isdir(path):
                args.path = path
            else:
                logging.error('file overlay directory "%s" does not exist',
                    path)
                raise utils.FatalException()

        if not '.' in args.fqdn:
            logging.error('"%s" is not a fully qualified domain name',
                args.fqdn)
            raise utils.FatalException()

        if not args.seed:
            args.seed = release
        args.seeds = [args.seed] + args.additional
        for seed_file in args.seeds:
            file_name = os.path.join(self.cfg['paths']['seeds'], seed_file)
            file_name += '.seed'
            if not os.path.isfile(file_name):
                logging.error('preseed file "%s" does not exist', file_name)
                raise utils.FatalException()

        return args, config

    def net(self, args):
        """process the net command"""
        _, release, _ = args.release.split('-')
        args, config = self._shared(args, release)

        path = os.path.join(config['paths']['tftpboot'], 'seedbank',
            args.release)
        if not os.path.isdir(path):
            if release in config['distributions']['netboots']:
                logging.error('"%s" is not available, run "seedbank manage -n '
                    '"%s" to download an prepare the release', args.release)
            else:
                logging.error('"%s" could not be find in the system settings',
                    args.release)
            raise utils.FatalException()

        if args.macaddress:
            if len(args.macaddress) == 12:
                pass
            elif not re.match('([a-fA-F0-9]{2}[:|\-]?){6}', args.macaddress):
                err = '"%s" is not a valid MAC address' % args.macaddress
                logging.error(err)
                raise utils.FatalException()
            else:
                args.address = utils.format_address(args.macaddress)
        else:
            ip_address = utils.resolve_ip_address(args.fqdn) 
            args.address = utils.ip_to_hex(ip_address)

        if args.puppet:
            for index, manifest in enumerate(args.puppet):
                file_name = os.path.join(config['paths']['puppet_manifests'],
                    manifest + '.pp')
                if not os.path.isfile(file_name):
                    err = 'Puppet manifest "%s" does not exist' % manifest
                    logging.error(err)
                    raise utils.FatalException()
                else:
                    args.puppet[index] = manifest

        pxe = net.GeneratePxe(args)
        pxe.state_remove()
        pxe.write(pxe.generate())
        pxe.hook_enable()
        
    def iso(self, args):
        """validate the input and if no errors are found build an (unattended)
        installation ISO from a regular install ISO"""
        if not 'seed' in args:
            args.seed = ''
        if not 'config' in args:
            args.config = ''
        if not 'puppet' in args:
            args.puppet = []

        _ , release, _, _ = args.release.split('-')
        args, config = self._shared(args, release)

        if args.release in config['distributions']['isos']:
            iso_file = os.path.join(config['paths']['isos'], args.release)
            iso_file += '.iso'
        else:
            logging.error('"%s" is not a valid release', args.release)
            raise utils.FatalException()

        iso_dst = os.path.abspath(args.output)
        if os.path.isfile(iso_dst):
            logging.warning('"%s" already exists, will overwrite', iso_dst)

        build = iso.Build(config, iso_file, args.fqdn, iso_dst)
        build.prepare()

        if args.puppet:
            build.add_puppet_manifests(args.fqdn)

        template_cfg = settings.template(args.fqdn, args.overlay, args.config,
            args.variables)

        if args.overlay:
            overlay = pimp.Overlay(self.cfg, args.overlay, args.fqdn)
            overlay.prepare(template_cfg['seed'])
            permissions = pimp.OverlayPermissions(self.cfg)
            permissions.script(overlay.dst, args.overlay, '/target')
 
        seed = pimp.SeedPimp(template_cfg, 'iso')
        preseed = seed.pimp(args.seeds, args.overlay, args.puppet)
        build.add_preseed(preseed)
        build.add_templates()
        if args.overlay:
            build.add_overlay(overlay.dst)
        build.create()

    def manage(self, args):
        """validate the input and if no errors are found run the specified 
        seedbank manage command actions"""
        setup = manage.Manage(self.cfg)
        if args.netboot:
            if args.netboot in self.cfg['distributions']['netboots']:
                setup.netboot(args.netboot)
            else:
                logging.error('"%s" is not configured (use "seedbank list '
                    '--netboots" to list available and downloaded netboot '
                    'images)', args.netboot)
                raise utils.FatalException()
        elif args.iso:
            if args.iso in self.cfg['distributions']['isos']:
                setup.iso(args.iso)
            else:
                logging.error('"%s" is not configured (use "seedbank list '
                    '--isos" to list available and downloaded ISOs)', args.iso)
                raise utils.FatalException()
        elif args.syslinux:
            setup.syslinux()
        elif args.remove:
            setup.remove(args.remove)
        elif args.overlay:
            permissions = pimp.OverlayPermissions(self.cfg)
            permissions.generate_all()

    def daemon(self, args):
        """start the seedBank daemon"""
        if args.start:
            rest.start()
            #daemon.start()
        elif args.bottle:
            rest.start()
