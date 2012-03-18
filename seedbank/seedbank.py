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

"""
todo
====
improve documentation
add validation for YAML configuration files
improve security, run as a different user, daemon hardening
default pxelinux config file generator

future
======
RedHat kickstart support?
freeDOS support?
more?
"""

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '2.0.0rc3'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import argparse
import logging
import logging.config
import sys

from argparse import RawTextHelpFormatter

import settings
import parse
import utils


cfg = settings.parse_cfg()
logging.config.fileConfig(cfg['logging']['configuration'])
logger = logging.getLogger(cfg['logging']['logger'])


def argument_parser():
    """process the arguments"""
    parse_arg = parse.ParseArguments(cfg)

    parser = argparse.ArgumentParser(description='seedBank - Debian/Ubuntu '
        'netboot installations the way it is meant to be... (c) 2009-2012 '
        'Jasper Poppe <jpoppe@ebay.com>', epilog='for more information visit: '
        'http://www.infrastructureanywhere.com', fromfile_prefix_chars='@')
    parser.add_argument('--version', action='version', version=__version__)
    subparsers = parser.add_subparsers(help='commands')

    parser_list = subparsers.add_parser('list',
        help='list resources like netboot images, seed files, Puppet '
        'manifests, configuration overrides, file overlays, pxelinux.cfg files'
        ', netboot images and ISOs', formatter_class=RawTextHelpFormatter)
    parser_list.add_argument('-a', '--all', action='store_true',
        help='List all resources')
    parser_list.add_argument('-n', '--netboots', action='store_true',
        help='list releases which are available for netboot\ninstallations'
        ', names starting with an asterisk are\nready to use\nnetboot images '
        'are managed by the "seedbank manage"\ncommand')
    parser_list.add_argument('-i', '--isos', action='store_true',
        help='list ISOs which are used for building (unattended)\ninstallation '
        'ISOs ISO names starting with an asterisk\nare ready to use\nISOs '
        'are managed by the "seedbank manage" command')
    parser_list.add_argument('-s', '--seeds',  action='store_true',
        help='list available seed files\nseed files are (partial) preseed ' 
        'files which are used\nfor providing answers to the installer\n'
        'default location: /etc/seedbank/seeds')
    parser_list.add_argument('-c', '--configs', action='store_true',
        help='list available configs\nconfigs are used for overriding the '
        'default configuration\nand providing default command line options '
        'for the\n"seedbank net" and "seedbank iso commands"\ndefault '
        'location: /etc/seedbank/configs')
    parser_list.add_argument('-o', '--overlays', action='store_true',
        help='list available overlays\nthe contents of an overlay directory '
        'will be copied over\nthe file system just before the end of an '
        'installation\ndefault location: /etc/seedbank/overlays')
    parser_list.add_argument('-m', '--manifests', action='store_true',
        help='list available Puppet manifests\nWhen you enable one or more '
        'Puppet manifests they will\nbe applied once by a stand alone Puppet '
        'instance,\ndirectly after the first boot of the machine\nwhich has '
        'been installed\ndefault location: /etc/seedbank/manifests')
    parser_list.add_argument('-p', '--pxe', action='store_true',
        help='list all "pxelinux.cfg" configs\npxelinux.cfg files are '
        'generated by the "seedbank net"\ncommand and are used to provide '
        'machine specific\ninformation to the installer after the machine '
        'PXE boots\nvia the network, the variables stored in those file\n'
        'comments are used by the seedBank daemon for\ngenerating the preseed '
        'file, those variables could also\nbe used in file overlay templates\n'
        'default location: /var/lib/tftpboot/pxelinux.cfg')
    parser_list.set_defaults(func=parse_arg.list)

    parser_shared = argparse.ArgumentParser(add_help=False)
    parser_shared.add_argument('-o', '--overlay',  default=None, help='file '
        'overlay which will be copied over the file system before the end of '
        'the installation')
    parser_shared.add_argument('-s', '--seed', help='override the default '
        'preseed file (the default preseed file has the name of the '
        'distribution, e.g: squeeze or precise)')
    parser_shared.add_argument('-a', '--additional', action='append',
        default=[], metavar='SEED', help='append additional seed files to the '
        'default seed file like  disk recipes, repositories or other '
        'additional (custom) seeds')
    parser_shared.add_argument('fqdn', help='fully qualified domain name of '
        'the node to install')
    parser_shared.add_argument('release', help='release name')
    parser_shared.add_argument('-m', '--manifests', action='append', default=[], 
        help='choose one or more Puppet manifest(s) to apply after the '
        'installation')
    parser_shared.add_argument('-c', '--config', default=None, help='override '
        'template (pxe and seed) settings')
  
    parser_net = subparsers.add_parser('net', parents=[parser_shared],
        help='manage netboot installations, prepare a pxelinux.cfg '
        'file with all the settings required for a netboot installation')
    parser_net.add_argument('-M', '--macaddress',
        help='use a MAC address instead of a to hexidecimal converted IP '
        'address for the pxelinux.cfg configuration file name, the advantage '
        'of this is there will be no DNS lookups needed')
    parser_net.add_argument('-v', '--variables', nargs=2, action='append',
        metavar=('KEY', 'VALUE'),
        default=[], help='add one or more additional pxe variables which '
        'will be stored in the generated pxelinux.cfg file and could be used '
        'by seedBank templates in the overlay directory and the disable and '
        'enable hooks')
    parser_net.set_defaults(func=parse_arg.net)

    parser_iso = subparsers.add_parser('iso', parents=[parser_shared],
        help='build an (unattended) installation ISO')
    parser_iso.add_argument('output', help='file name of the generated ISO')
    parser_iso.add_argument('-v', '--variables', nargs=2, action='append',
        metavar=('KEY', 'VALUE'),
        default=[], help='add (or overrides) one or more seed and or overlay '
        'variables which could be used by seedBank templates in the overlay '
        'directory and preseed files')
    parser_iso.set_defaults(func=parse_arg.iso)

    parser_manage = subparsers.add_parser('manage', help='download and '
        'manage netboot images, syslinux files and ISOs')
    group = parser_manage.add_mutually_exclusive_group() 
    group.add_argument('-s', '--syslinux', action='store_true',
        help='download the syslinux archive and extract the pxelinux.0, '
        'menu.c32 and vesamenu.c32 files and place those in the tftpboot '
        'directory. (those files are required for doing a PXE boot)')
    group.add_argument('-n', '--netboot', action='store', metavar='RELEASE',
        help='download and prepare a netboot image, when the release has been '
        'defined in the distributions -> firmware section Debian "non free" '
        'firmware files will be integrated into the netboot image, the '
        'contents of the netboot archive will be placed in the configured '
        'tftpboot path')
    group.add_argument('-i', '--iso', action='store', metavar='RELEASE',
        help='download ISO images which are used by the "seedbank iso command"')
    group.add_argument('-r', '--remove', action='store', metavar='RELEASE',
        help='remove an iso or netboot images from the tftpboot and seedBank '
        'archives directories')
    group.add_argument('-o', '--overlay', action='store_true',
        help='update or create <overlay>.permissions for all overlaysi, those '
        'files contain user, group and permissions which will be set by a '
        'dynamically generated script just before the end of an installation'
        'after the overlay got applied')
    group.set_defaults(func=parse_arg.manage)

    parser_daemon = subparsers.add_parser('daemon', help='seedBank daemon')
    parser_daemon.add_argument('-s', '--start', action='store_true',
        help='start the seedBank daemon which provides dynamically resources '
        'used by the installer, it also takes care of disabling the pxelinux '
        'configuration files after a successfull installation')
    parser_daemon.add_argument('-b', '--bottle', action='store_true',
        help='start the bottle')
    parser_daemon.set_defaults(func=parse_arg.daemon)

    args = parser.parse_args()
    logging.debug('given arguments: %s', args)

    if len(sys.argv) == 2:
        if sys.argv[1] == 'list':
            parser_list.print_help()
        if sys.argv[1] == 'manage':
            parser_manage.print_help()
        if sys.argv[1] == 'daemon':
            parser_daemon.print_help()
    else:
        args.func(args)

def main():
    """the main application"""

    try:
        #if sys.stdin.isatty():
        argument_parser()
        #else:
        #    piped = sys.stdin.read()
        #    print(piped)
    except utils.FatalException:
        sys.exit(1)
    except Exception as err:
        logger.exception(err)
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except SystemExit as err:
        sys.exit(err.code)
    except KeyboardInterrupt:
        sys.stderr.write('info: cancelled by user\n')
        sys.exit(1)
