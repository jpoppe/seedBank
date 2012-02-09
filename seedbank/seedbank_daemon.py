#!/usr/bin/env python

"""

seedBank daemon

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

Testing URLs:
  wget 'http://192.168.0.1:7467/seed?seed=squeeze&host=host001&domain=foo.com&address=C0A80014&recipe=web' -q -O -
  wget 'http://192.168.0.1:7467/manifests.tgz'
  wget 'http://192.168.0.1:7467/bootstrapinit?address=C0A80014' -q -O -
  wget 'http://192.168.0.1:7467/pimp?address=C0A80014' -q -O -
  wget 'http://192.168.0.1:7467/daemon?address=C0A80014&recipe=web' -q -O -
  wget 'http://192.168.0.1:7467/overlay.tgz?address=C0A80014' -O overlay.tgz
  wget 'http://192.168.0.1:7467/files?file=test'
  wget 'http://192.168.0.1:7467/disable?address=C0A80014' -q -O
  wget 'http://192.168.0.1:7467/status?address=C0A80014&state=done' -q -O

"""

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '1.1.0'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import cgi
import cStringIO
import copy
import fnmatch
import logging
import optparse
import os
import seedlib
import shutil
import string
import sys
import tarfile
import urlparse

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

sys.path.append('/etc/seedbank')
from settings import server, settings, sp_paths, settings_seedfile, settings_manifests

"""log settings"""
logging.basicConfig(
    filename = settings['log_file'],
    #filename = '/dev/stdout',
    format = '%(asctime)s %(levelname)-10s %(message)s',
    datefmt = '%b %d %H:%M:%S',
    level = logging.INFO
)
log = logging.getLogger('seeddaemon')

def directory_to_tar_gz(directory):
    """tar, gzip a directory and return tgz file"""
    current_cwd = os.getcwd()
    os.chdir(directory)
    try:
        tar_file = cStringIO.StringIO()
        tar = tarfile.open(fileobj=tar_file, mode='w:gz')
        tar.add('.')
        tar.close()
        os.chdir(current_cwd)
    except:
        print ('error: creating tarball of "%s" failed' % directory)
        return
    else:
        return tar_file.getvalue()


class MyTemplate(string.Template):
    """override default delimiter $ with *"""
    delimiter = '*'


class SeedConstruct(object):
    """generate the seedfile"""

    def generate(self, query, pxe_vars):
        """generate the seedfile"""
        files = [os.path.join(sp_paths['seeds'], query['seed'][0] + '.seed')]

        if query.has_key('recipe'):
            files += [os.path.join(sp_paths['recipes'], recipe) for recipe in query['recipe']]

        if pxe_vars.has_key('seedbank_seeds'):
            files += [os.path.join(sp_paths['seeds'], seed + '.seed') for seed in pxe_vars['seedbank_seeds'].split(',')]

        contents = ''
        for filename in files:
            if not os.path.isfile(filename):
                log.error('could not open file "%s"' % filename)
                return
            else:
                contents += seedlib.read_file(filename)

        return contents

    def udebs(self, pxe_vars, values):
        """custom udebs support"""
        udebs_command = []
        command = 'wget \'http://%s:%s/udebs?file=${filename}.udeb\' -O /tmp/${filename}.udeb' % (server['address'], server['port'])
        install_command = 'udpkg --unpack /tmp/*.udeb'

        if pxe_vars.has_key('seedbank_udebs'):
            if pxe_vars['seedbank_udebs']:
                for udeb in pxe_vars['seedbank_udebs'].split(','):
                    udebs_command.append(command.replace('${filename}', udeb))

                if udebs_command:
                    udebs_command.append(install_command)
                    udebs_command = '; '.join(udebs_command)

                    if values['earlycommand']:
                        values['earlycommand'] = udebs_command + '; ' + values['earlycommand']
                    else:
                        values['earlycommand'] = udebs_command

        return values

    def bootstrap(self, pxe_vars, values):
        """add bootstrap commands to latetecommand if manifests or partitioner is enabled """
        bootstrap = False

        if pxe_vars.has_key('seedbank_manifests') and pxe_vars['seedbank_manifests']:
            bootstrap = True
        elif pxe_vars.has_key('seedbank_partitioner') and pxe_vars['seedbank_partitioner']:
            bootstrap = True

        if bootstrap:
            if values['latecommand']:
                values['latecommand'] = values['bootstrapcommand'] + '; ' + values['latecommand']
            else:
                values['latecommand'] = values['bootstrapcommand']

        return values

    def overlay(self, pxe_vars, values):
        """process late command for overlay"""
        if pxe_vars.has_key('seedbank_manifests') and pxe_vars.has_key('seedbank_overlay'):
            if pxe_vars['seedbank_overlay']:
                if values['latecommand']:
                    values['latecommand'] = values['overlayscommand'] + '; ' + values['latecommand']
                else:
                    values['latecommand'] = values['overlayscommand']
        return values


class ProcessRequest(object):
    """process the HTTP request"""

    def __init__(self):
        """initialize class variables"""
        self.info = False
        self.error = False
        self.contents = False

    def bootstrapinit(self, address, pxe_vars):
        """generate the bootstrap init file which is used for puppet manifests and the seedbank partitioner"""
        m_commands = ''
        p_commands = []
        call_functions = []

        if pxe_vars.has_key('seedbank_partitioner') and pxe_vars['seedbank_partitioner']:
            p_commands.append('wget http://%s:%s/recipes?file=%s.extended -O /tmp/seedbank_recipe' % (server['address'], server['port'], pxe_vars['seedbank_partitioner']))
            p_commands.append('\twget http://%s:%s/recipes?file=seedbank_partitioner.py -O /tmp/seedbank_partitioner.py' % (server['address'], server['port']))
            p_commands.append('\tpython /tmp/seedbank_partitioner.py -r /tmp/seedbank_recipe')
            p_commands.append('\trm /tmp/seedbank_partitioner.py')
            p_commands.append('\trm /tmp/seedbank_partitioner.sh')
            p_commands.append('\trm /tmp/seedbank_recipe')
            call_functions.append('partitioner')

        if pxe_vars.has_key('seedbank_manifests') and pxe_vars['seedbank_manifests']:
            manifests = pxe_vars['seedbank_manifests'].split(',')
            command = settings_manifests['command'] 
            m_commands = [command.replace('${manifest}', manifest + '.pp') for manifest in manifests]
            m_commands = '\n'.join(m_commands)
            call_functions.append('manifests')

        if call_functions:
            template_file = os.path.join(sp_paths['templates'], settings_manifests['template'])
            contents = string.Template(seedlib.read_file(template_file))
            values = {
                'manifests_commands': m_commands,
                'partitioner_commands': '\n'.join(p_commands),
                'call_functions': '\n'.join(call_functions),
                'server': server['address'],
                'port': server['port']
            }
            self.contents = contents.substitute(values)
            self.info = 'generated the bootstrap init file successfully'
        else:
            self.error = 'failed to generate the bootstrap init file'

        return (self.info, self.error, self.contents)
     
    def add_log_entry(self, address, message):
        """write a custom log entry"""
        self.info = message
        return (self.info, self.error, self.contents)

    def write_status(self, address, state, pxe_vars):
        """write a file with custom status"""
        self.info = 'setting state to "%s"' % state
        file_name = '%s_%s.state' % (pxe_vars['seedbank_fqdn'], state)
        file_name = os.path.join(sp_paths['status'], file_name)

        try:
            data = open(file_name, 'w')
        except Exception:
            self.error = Exception
        else:
            data.close()
            self.info = '"%s" has been written' % file_name

        return (self.info, self.error, self.contents)

    def disable(self, pxe_file):
        """disable a pxe host"""
        destination = pxe_file + '.disabled'
        try:
            shutil.move(pxe_file, destination)
        except (IOError, os.error):
            self.error = 'moving "%s" to "%s" failed' % (pxe_file, destination)
        else:
            self.info = 'disabled host "%s"' % (pxe_file)
        return (self.info, self.error, self.contents)

    def seed(self, address, query, pxe_vars):
        """generate the seedfile"""
        mandatory = ['seed', 'host', 'domain']
        for item in mandatory:
            if not query.has_key(item):
                self.error = 'you need to specify "%s" in the querystring with "seed"' % item
                return (self.info, self.error, self.contents)

        construct = SeedConstruct()
        seedfile = construct.generate(query, pxe_vars)

        if seedfile:
            values = {'hostname': query['host'][0], 'domainname': query['domain'][0]}

            new_settings_seedfile = copy.deepcopy(settings_seedfile)
            for key, value in new_settings_seedfile.items():
                if 'command' in key:
                    contents = string.Template(value)
                    new_value = contents.substitute({'address': address})
                    new_settings_seedfile[key] = new_value

            values.update(new_settings_seedfile)
            values = construct.udebs(pxe_vars, values)
            values = construct.bootstrap(pxe_vars, values)
            values = construct.overlay(pxe_vars, values)
           
            contents = MyTemplate(seedfile)
            self.contents = contents.substitute(values)
            self.info = 'generated seed file for "%s"' % address
        else:
            self.error = 'seedfile generation failed'

        return (self.info, self.error, self.contents)

    def pimp(self, address):
        """this function gets called by the installer will write to log"""
        self.info = 'starting installation for "%s"' % address 
        return (self.info, self.error, self.contents)

    '''
    # unused, could maybe be used when using seedbank_partitioner for creating
    # debian recipes
    def recipe(self, address, pxe_vars):
        """read an extended recipe and return shell script for partitioning"""
        filename = os.path.join(sp_paths['recipes'], pxe_vars['seedbank_partitioner']) + '.extended'
        contents = seedbank_partitioner.generate(filename)
        self.info = 'generated partitioning script for %s' % filename
        return (self.info, self.error, contents)
    '''

    def manifests(self):
        """create an archive with all manifests"""
        contents = directory_to_tar_gz(sp_paths['manifests'])
        if contents:
            self.contents = contents
            self.info = 'generated tar gz archive successfully'
        else:
            self.error = 'creating tar gz for "%s" failed' % sp_paths['manifests']
        return (self.info, self.error, self.contents)

    def overlay(self, address, pxe_vars):
        """create archive with files from selected overlay and apply templates
        to .sptemplate files, the variables will be read from the host related
        pxe file, the "seedbank_" prefix will be stripped from the variables """
        path = os.path.join(sp_paths['overlays'], pxe_vars['seedbank_overlay'])
        if not os.path.isdir(path):
            self.error = 'directory "%s" does not exist' % path
            return (self.info, self.error, self.contents)

        template_values = dict((key.replace('seedbank_', ''), value) for key, value in pxe_vars.items())

        destination = os.path.join('/tmp', 'seedbank_' + address)
        if os.path.isdir(destination):
            try:
                shutil.rmtree(destination)
            except (IOError, OSError):
                self.error = 'failed to remove the temporary directory "%s"' % destination
                return (self.info, self.error, self.contents)

        try:
            shutil.copytree(path, destination)
        except (IOError, OSError):
            self.error = 'failed to copy overlay "%s"' % destination
            return (self.info, self.error, self.contents)

        templates_list = []
        for root, dirs, files in os.walk(destination):
            for file in files:
                if fnmatch.fnmatch(file, '*.sptemplate'):
                    templates_list.append(os.path.join(root, file))

        for filename in templates_list:
            data = open(filename, 'r').read()
            try:
                data = seedlib.apply_template(data, template_values)
            except KeyError as error:
                self.error = 'failed to apply template on "%s", variable "%s" has not been defined' % (filename, error)
                return (self.info, self.error, self.contents)

            try:
                file = open(filename, 'w')
            except (IOError, OSError):
                self.error = 'failed to open "%s" for writing' % filename
                return (self.info, self.error, self.contents)
            else:
                file.write(data)
                file.close()

            try:
                os.rename(filename, filename.replace('.sptemplate', ''))
            except (IOError, OSError):
                self.error = 'failed to rename "%s"' % filename
                return (self.info, self.error, self.contents)

        contents = directory_to_tar_gz(destination)
        if contents:
            self.contents = contents
            self.info = 'generated tar gz archive successfully'
        else:
            self.error = 'creating tar gz for "%s" failed' % destination

        return (self.info, self.error, self.contents)

    def file(self, query, selection):
        """internal web/file server"""
        if not query.has_key('file'):
            self.error = 'the file query string is missing'
        else:
            filename = query['file'][0]
            filename = os.path.basename(filename)
            filename = os.path.join(sp_paths[selection], filename)
            self.info = 'requesting file "%s"' % filename
            contents = seedlib.read_file(filename)
            if contents:
                self.contents = contents
            else:
                self.error = 'reading file "%s" failed' % filename
        return (self.info, self.error, self.contents)


class GetHandler(BaseHTTPRequestHandler):
    """override BaseHTTPRequestHandler"""

    def log_message(self, format, *args):
        """add logging"""
        print (args)
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(),
                            self.log_date_time_string(), format%args))
        log.info("%s - %s" % (self.address_string(), format%args))

    def check_pxe_file(self, pxe_file):
        """check if the pxe file exists"""
        if not os.path.isfile(pxe_file):
            error = 'pxe file "%s" not found' % pxe_file
            self.wfile.write(error + '\n\n')
            self.send_response(404)
            log.error(error)
            return True

    def read_pxe_variables(self, pxe_file):
        """read all seedbank variables from the pxe file"""
        try:
            data = seedlib.read_file(pxe_file)
            data = [line[2:] for line in data.split('\n') if line.startswith('# seedbank_') or line.startswith('# external_')]
            data = [line.split(' = ', 1) for line in data]
            result = {}
            for entry in data:
                result[str(entry[0])] = entry[1]
            return result
        except Exception:
            return

    def do_GET(self):
        """process the url path and take action"""
        parsed_path = urlparse.urlparse(self.path)
        query = cgi.parse_qs(parsed_path.query)

        # security fix
        for key in query:
            values = [os.path.basename(value) for value in query[key]]
            query[key] = values

        paths = parsed_path.path[1:].split('/')
        process = ProcessRequest()
        selection = paths.pop(0)
        error = False

        need_address = ['seed', 'overlay.tgz', 'bootstrapinit', 'disable', 'pimp', 'status']
        if query.has_key('address'):
            address = query['address'][0]
            pxe_file = os.path.join(sp_paths['tftpboot'], 'pxelinux.cfg', address)
            if not os.path.isfile(pxe_file):
                pxe_file = pxe_file + '.disabled'

            if not os.path.isfile(pxe_file):
                error = 'pxe file "%s" does not exist' % pxe_file
            else:
                pxe_vars = self.read_pxe_variables(pxe_file)
        elif selection in need_address:
            error = 'you need to specify an address in the querystring with "%s"' % selection

        if not error:
            if selection == 'pimp':
                info, error, contents = process.pimp(address)
            elif selection == 'seed':
                info, error, contents = process.seed(address, query, pxe_vars)
            elif selection == 'recipes':
                info, error, contents = process.file(query, selection)
            elif selection == 'manifests.tgz':
                info, error, contents = process.manifests()
            elif selection == 'overlay.tgz':
                info, error, contents = process.overlay(address, pxe_vars)
            elif selection == 'bootstrapinit':
                info, error, contents = process.bootstrapinit(address, pxe_vars)
            elif selection == 'disable':
                info, error, contents = process.disable(pxe_file)
            elif selection == 'log':
                info, error, contents = process.add_log_entry(self.address_string(), query['message'][0])
            elif selection == 'status':
                info, error, contents = process.write_status(self.address_string(), query['state'][0], pxe_vars)
            elif selection == 'files' or selection == 'udebs':
                info, error, contents = process.file(query, selection)
            else:
                info, error, contents = (False, '"%s" is an unknown request' % selection, False)

        if error:
            self.wfile.write(error + '\n\n')
            self.send_response(404)
            log.error(error)
        else:
            if info:
                log.info(info)
            else:
                contents = info
            self.send_response(200)
            self.end_headers()
            self.wfile.write(contents)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """multithread webserver"""


def main():
    """main application, this function won't called when used as a module"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for path in sp_paths:
        if not sp_paths[path].startswith('/'):
            sp_paths[path] = os.path.join(base_dir, sp_paths[path])

    parser = optparse.OptionParser(prog='seedbank_daemon', version=__version__)
    parser.set_description ('seedBank daemon (c) 2009-2012 Jasper Poppe <jpoppe@ebay.com>')
    parser.set_usage('%prog [-d]')
    parser.add_option('-d', '--daemon', dest='daemon', help='run in daemon mode', action='store_true')
    (opts, args) = parser.parse_args()

    if args:
        parser.error('the seedbank daemon does not take any arguments')
    elif opts.daemon:
        print ('info: starting multithreaded seedbank daemon at port %s, use <ctrl-c> to stop' % server['port'])
        log.info('starting multithreaded seedbank daemon')
        httpd = ThreadedHTTPServer((server['listen'], int(server['port'])), GetHandler)
        httpd.serve_forever()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
