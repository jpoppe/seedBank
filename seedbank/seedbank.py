#!/usr/bin/env python

"""

Copyright 2009-2012 Jasper Poppe <jpoppe@ebay.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

todo
====

enable the seedbank_partitioner script again
improve security, run as different user, daemon hardening
fix override option for daemon variables (-c) (requires quite some changes)
more verbose try messages
catch errors when wrong user permissions are used

additional
==========

more structured error handling in input validation
improve documentation
default pxe generator
nginx support
better structured code

future
======

Solaris jumpstart/RedHat kickstart support?
add freeDOS support?
more?

"""

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '1.1.0'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import optparse
import os
import re
import seedlib
import socket
import string
import sys
import urllib
import yaml

sys.path.append('/etc/seedbank')

from settings import sp_paths, server, settings, settings_pxe, hooks_enable, external_nodes

class ManagePxe(object):
    """manage and generate pxe files"""

    def _rmfile(self, filename):
        """if file exists, delete file"""
        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except IOError:
                print ('error: can not remove file "%s"' % filename)
                return
            else:
                print ('info: file "%s" has been removed' % filename)

        return True

    def _writefile(self, filename, contents):
        """(over)write contents to filename"""
        if os.path.isfile(filename):
            print ('warning: file "%s" will be overwritten since it already exists' % filename)

        try:
            f = open(filename, 'w')
            f.write(contents)
        except IOError:
            print ('error: opening of file "%s" failed' % filename)
            return
        else:
            print ('info: file "%s" has been written' % filename)

        return True

    def _construct_query(self, address, release, seed, recipes, hostname, domainname):
        """generate the url path"""
        if not seed: 
            seed = release.split('-')[1]

        query = [('seed', seed), ('address', address), ('host', hostname), ('domain', domainname)]
        if recipes:
            for recipe in recipes:
                query.append(('recipe', recipe))

        return urllib.urlencode(query)

    def create(self, opts, hostname, domainname, address, release, external):
        """generate the pxe boot file"""

        seed = opts.seed
        if opts.seed_additional:
            seed_additional = ','.join(opts.seed_additional)
        else:
            seed_additional = []
        recipes = opts.recipes
        overlay = opts.overlay
        udebs = opts.udebs
        manifests = opts.manifests
        pxevariables = opts.pxevariables

        if not os.path.isdir(sp_paths['status']):
            print ('error: seedBank status directory "%s" does not exist' % sp_paths['status'])
            sys.exit(1)

        file_prefix = '%s.%s_' % (hostname, domainname)
        for file_name in os.listdir(sp_paths['status']):
            if file_name.startswith(file_prefix) and file_name.endswith('.state'):
                target = os.path.join(sp_paths['status'], file_name)
                try:
                    os.unlink(target)
                except Exception:
                    print ('error: failed to delete "%s"' % target)
                    sys.exit(1)
                else:
                    print ('info: removed state file "%s"' % target)

        partitioner = ''

        if overlay and external:
            external = ['# %s = %s' % (k, v) for k, v in external.items()]
            overlay += '\n#\n'
            overlay += '\n'.join(external)
        elif overlay:
            overlay += '\n#\n'
        else:
            overlay = ''

        if udebs:
            udebs = ','.join(udebs)
        else:
            udebs = ''

        if manifests:
            manifests = ','.join(manifests)
        else:
            manifests = ''

        variables = []
        if pxevariables:
            for values in pxevariables:
                variables.append('# seedbank_%s = %s' % (values[0], values[1]))
            variables = '\n'.join(variables)

        if recipes:
            for recipe in recipes:
                filename = os.path.join(sp_paths['recipes'], recipe + '.extended')
                if os.path.isfile(filename):
                    partitioner = recipe

        values = {
            'seeds': seed_additional,
            'seed_host': server['address'],
            'seed_port': server['port'],
            'address': address,
            'overlay': overlay,
            'manifests': manifests,
            'partitioner': partitioner,
            'udebs': udebs,
            'hostname': hostname,
            'domainname': domainname,
            'fqdn': hostname + '.' + domainname,
            'query': self._construct_query(address, release, seed, recipes, hostname, domainname),
            'kernel': '%s/%s/%s' % ('seedbank', release, 'linux'),
            'initrd': '%s/%s/%s' % ('seedbank', release, 'initrd.gz')
        }
        values.update(settings_pxe)

        filename = os.path.join(sp_paths['templates'], 'pxe-' + release.split('-')[0])
        if not os.path.isfile(filename):
            print ('error: file "%s" not found (hint: check /etc/seedbank/settings.py)' % filename)
        else:
            contents = seedlib.read_file(filename)
            contents = string.Template(contents)
            if contents:
                contents = contents.substitute(values)
                if variables:
                    contents = contents + variables + '\n'
                return contents

    def write(self, filename, contents):
        """write the pxe boot file"""
        pxefile = os.path.join(sp_paths['tftpboot'], 'pxelinux.cfg', filename)
        path = os.path.dirname(pxefile)

        if not seedlib.makedirs(path):
            return
        elif not self._rmfile('%s.disabled' % pxefile):
            return
        elif not self._writefile(pxefile, contents):
            return
        else:
            return True


class ProcessInput(object):
    """process the input"""

    def __init__(self):
        """initialize class variables"""
        self.filename = False

    def _validate(self, value, path):
        """check if file is in directory"""
        if not os.path.isdir(path):
            return
        elif value in os.listdir(path):
            return True

    def _get_address(self, host):
        """resolve ip address for a host"""
        try:
            address = socket.gethostbyname(host)
        except socket.error:
            return
        else:
            return address

    def _get_hostname(self, host):
        """resolve hostname for a host"""
        try:
            hostname = socket.gethostbyaddr(host)[0]
        except socket.error:
            return
        else:
            return hostname

    def _ip2hex(self, address):
        """convert ip to hex"""
        return ''.join(['%02X' % int(octet) for octet in address.split('.')])

    def validate_release(self, release):
        """check if tftp files are available for the chosen release""" 
        validate = self._validate(release, os.path.join(sp_paths['tftpboot'], 'seedbank'))
        if not validate:
            return True

    def validate_seed(self, seed):
        """check if the seed file is available"""
        if seed:
            return self._validate(seed + '.seed', sp_paths['seeds'])
        else:
            return True

    def validate_recipes(self, recipes):
        """check if chosen recipe exists"""
        for recipe in recipes:
            validate = self._validate(recipe, sp_paths['recipes'])
            if not validate:
                return
        return True

    def validate_manifests(self, manifests):
        """check if chosen manifests exists"""
        for manifest in manifests:
            validate = self._validate(manifest + '.pp', sp_paths['manifests'])
            if not validate:
                return manifest

    def validate_udebs(self, udebs):
        """check if chosen udebs exists"""
        for udeb in udebs:
            validate = self._validate(udeb + '.udeb', sp_paths['udebs'])
            if not validate:
                return udeb

    def validate_overlay(self, overlay):
        """check if chosen overlay exists"""
        if overlay:
            validate = self._validate(overlay, sp_paths['overlays'])
            if not validate:
                return overlay

    def host_by_name(self, host):
        """return ip address converted to hex, hostname and domainname"""
        fqdn = socket.getfqdn(host)
        address = self._get_address(host)
        if not address:
            raise
        else:
            return self.return_host(fqdn, self._ip2hex(address))

    def host_by_mac(self, fqdn, address):
        """return mac address, hostname and domainname"""
        if len(address) == 12:
            pass
        elif not re.match('([a-fA-F0-9]{2}[:|\-]?){6}', address):
            return
        return self.return_host(fqdn, seedlib.format_address(address))

    def host_by_ip(self, address):
        """return ip address converted to hex, hostname and domainname"""
        try:
            socket.inet_aton(address)
        except socket.error:
            raise

        fqdn = self._get_hostname(address)
        if not fqdn:
            return
        else:
            print ('info: fqdn for "%s" is "%s"' % (address, fqdn))
            return self.return_host(fqdn, self._ip2hex(address))

    def return_host(self, fqdn, address):
        hostname, domainname = seedlib.get_domain(fqdn)
        return address, hostname, domainname


class Hooks(object):
    """enable and disable hooks"""

    def __init__(self, values):
        """initialize variables"""
        self.values = values

    def run(self, hooks):
        """check if hooks are enabled and run a hook"""
        if settings['disable_hooks']:
            return

        queue = []
        for value in hooks.values():
            value = seedlib.apply_template(value, self.values)
            queue.append(value)
        
        for command in queue:
            print ('info: running hook "%s"' % command)
            seedlib.run_pipe(command)


class ExternalNodes(object):
    """use external nodes for getting configuration details"""
    
    def __init__(self, provider, values):
        """initialize variables"""
        self.provider = provider
        self.values = values

    def _gather_http(self):
        """get internal nodes information via http ot https"""
        url = seedlib.apply_template(self.provider, self.values)
        try:
            output = seedlib.read_url(url, 1)
        except Exception:
            return
        else:
            return self._return(yaml.load(output))

    def _return(self, result):
        if result:
            return dict([('external_' + k, v) for k, v in result.items()])
        else:
            print ('warning: no external node information found')

    def _gather_script(self):
        """get node information via a lookup script"""
        command = seedlib.apply_template(self.provider, self.values)
        command = command.split(' ')
        result = seedlib.run(command)
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


def list_releases():
    """list available releases, recipes, manifests, overlays"""
    list = seedlib.FormatListDir('releases')
    list.listdir(os.path.join(sp_paths['tftpboot'], 'seedbank'), 'dirs')
    list.show()
    print ('')
    list = seedlib.FormatListDir('recipes')
    list.listdir(sp_paths['recipes'], 'files', '.extended')
    list.show()
    print ('')
    list = seedlib.FormatListDir('manifests')
    list.listdir(sp_paths['manifests'], 'files')
    list.rstrip('.pp')
    list.show()
    print ('')
    list = seedlib.FormatListDir('udebs')
    list.listdir(sp_paths['udebs'], 'files')
    list.rstrip('.udeb')
    list.show()
    print ('')
    list = seedlib.FormatListDir('overlays')
    list.listdir(sp_paths['overlays'], 'dirs')
    list.show()
    print ('')
    list = seedlib.FormatListDir('seeds')
    list.listdir(sp_paths['seeds'], 'files')
    list.rstrip('.seed')
    list.show()

def list_pxe_files():
    '''list the seedbank managed file in pxelinux.cfg'''
    list = seedlib.FormatListDir('pxe files')
    list.listdir(os.path.join(sp_paths['tftpboot'], 'pxelinux.cfg'), 'files')
    list.show()

def override_settings(overrides):
    """override settings from settings.py"""
    for entry in overrides:
        try:
            category, key, value = entry.split(':', 2)
        except Exception:
            return '"%s" is not a valid custom override, check syntax' % entry

        if not globals().has_key(category):
            return 'settings has not a category named "%s"' % category

        if globals()[category].has_key(key):
            print ('info: "%s:%s" has been overridden with "%s"' % (category, key, value))
            globals()[category][key] = value
        else:
            return 'category "%s" in settings has no key "%s"' % (entry, key)

def main():
    """main application, this function won't called when used as a module"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for path in sp_paths:
        if not sp_paths[path].startswith('/'):
            sp_paths[path] = os.path.join(base_dir, sp_paths[path])

    parser = optparse.OptionParser(prog='seedbank', version=__version__)

    parser.set_description('seedbank - Debian/Ubuntu netboot installations the way it\'s meant to be\
                            (c) 2009-2012 Jasper Poppe <jpoppe@ebay.com>')

    parser.set_usage('%prog [-e]|[-M macaddress] [-r recipe] [-o overlay] [-m manifest] [-s seed] [-c override] <fqdn> <release>|-l|-p')
    parser.add_option('-M', '--macaddress', dest='macaddress', help='use mac address as pxe filename')
    parser.add_option('-e', '--externalhost', dest='externalhost', help='get the node information from an external source', action='store_true')
    parser.add_option('-l', '--list', dest='list', help='list available releases, (disk) recipes and manifests', action='store_true')
    parser.add_option('-r', '--recipe', dest='recipes', help='choose (disk) recipe(s)', action='append')
    parser.add_option('-m', '--manifest', dest='manifests', help='choose Puppet manifest(s) to apply after the installation', action='append')
    parser.add_option('-o', '--overlay', dest='overlay', help='choose an overlay from which files/templates should be copied')
    parser.add_option('-u', '--udeb', dest='udebs', help='choose custom udebs to use in the installer', action='append')
    parser.add_option('-s', '--seed', dest='seed', help='override default seed file (default: distribution name)')
    parser.add_option('-a', '--seed-additional', dest='seed_additional', help='append additional seed files to the default seed file', action='append')
    parser.add_option('-c', '--custom', dest='custom', help='override setting(s) from settings.py (dict:key:\'new_value\')', action='append')
    parser.add_option('-p', '--listpxefiles', dest='pxefiles', help='list all pxe host configs', action='store_true')
    parser.add_option('-v', '--variables', dest='pxevariables', help='specify additional pxe variables, (name value)', action='append', nargs=2)

    (opts, args) = parser.parse_args()

    if opts.custom:
        error = override_settings(opts.custom)
        if error:
            parser.error(error)

    if opts.list:
        list_releases()
        sys.exit(0)
    elif opts.pxefiles:
        list_pxe_files()
        sys.exit(0)
    elif not args:
        parser.print_help()
        sys.exit(0)
    elif not len(args) == 2:
        parser.error('you need to specify 2 arguments (fqdn|ip and a release), use -h for help')
        
    target, release = args
    process = ProcessInput()

    if process.validate_release(release):
        parser.error('%s is an unknown release (use -l to list available releases)' % release)

    if opts.macaddress:
        try:
            address, hostname, domainname = process.host_by_mac(target, opts.macaddress)
        except Exception:
            parser.error('"%s" is not a valid MAC address' % opts.macaddress)
    elif opts.externalhost:
        if external_nodes['provider']:
            hostname, domainname = seedlib.get_domain(args[0])
        else:
            parser.error('a provider needs to be specified in settings.py '
                            'in the external_nodes section')
    else:
        try:
            address, hostname, domainname = process.host_by_ip(target)
        except:
            try:
                address, hostname, domainname = process.host_by_name(target)
            except:
                parser.error('reverse DNS lookup for "%s" failed' % target)

    host_dict = {'hostname': hostname, 'domainname': domainname}

    if opts.externalhost:
        if external_nodes['provider']:
            external = ExternalNodes(external_nodes['provider'], host_dict)
            external_vars = external.gather()
            if not external_vars:
                parser.error('failed to gather information via "%s"' % external_nodes['provider'])

        address = external_vars[external_nodes['address']]
        address = seedlib.format_address(address)
    else:
        external_vars = ''

    pxe = ManagePxe()

    if opts.seed_additional:
        for additional in opts.seed_additional:
            if not process.validate_seed(additional):
                parser.error('seed file "%s/%s.seed" does not exist' % (sp_paths['seeds'], additional))

    if not process.validate_seed(opts.seed):
        parser.error('seed file "%s/%s.seed" does not exist' % (sp_paths['seeds'], opts.seed))

    if opts.recipes and not process.validate_recipes(opts.recipes):
        parser.error('"%s" is/are unknown recipe(s) (use -l to list available recipes)' % ', '.join(opts.recipes))

    if opts.manifests and process.validate_manifests(opts.manifests):
        manifest = process.validate_manifests(opts.manifests)
        parser.error('"%s" is an unknown manifest (use -l to list available manifests)' % (manifest))

    if opts.udebs and process.validate_udebs(opts.udebs):
        udeb = process.validate_udebs(opts.udebs)
        parser.error('"%s" is an unknown udeb (use -l to list available udebs)' % (udeb))

    if opts.overlay and process.validate_overlay(opts.overlay):
        overlay = process.validate_overlay(opts.overlay)
        parser.error('"%s" is an unknown overlay (use -l to list available overlays)' % (overlay))

    contents = pxe.create(opts, hostname, domainname, address, release, external_vars)
    if not contents:
        parser.error('failed to generate pxe file')

    if not pxe.write(address, contents):
        parser.error('can not write pxe file (hint: do you have the right permissions?')

    hooks = Hooks(host_dict)
    hooks.run(hooks_enable)

if __name__ == '__main__':
    main()
