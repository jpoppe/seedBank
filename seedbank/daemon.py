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
"""

"""
Testing URLs:
  wget 'http://localhost:7467/seed?address=C0A80014' -q -O -
  wget 'http://localhost:7467/manifests.tgz'
  wget 'http://localhost:7467/bootstrapinit?address=C0A80014' -q -O -
  wget 'http://localhost:7467/pimp?address=C0A80014' -q -O -
  wget 'http://localhost:7467/overlay.tgz?address=C0A80014' -O overlay.tgz
  wget 'http://localhost:7467/files?file=test'
  wget 'http://localhost:7467/disable?address=C0A80014' -q -O
  wget 'http://localhost:7467/status?address=C0A80014&state=done' -q -O

"""

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '2.0.0rc3'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import ast
import logging
import os
import re
import sys
import urlparse

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

import parse
import pimp
import settings
import utils

cfg = settings.parse_cfg()


class ProcessRequest:
    """process the HTTP request"""

    def bootstrapinit(self, pxe_vars):
        """generate the bootstrap init file which is used for puppet manifests
        and the seedbank partitioner"""
        commands = ''
        call_functions = []
        command = '; '.join(cfg['bootstrap']['puppet'])
        commands = [command.replace('${manifest}', manifest + '.pp')
            for manifest in pxe_vars['manifests']]
        commands = '\n'.join(commands)
        call_functions.append('manifests')

        if call_functions:
            template_file = os.path.join(cfg['paths']['templates'],
                cfg['templates']['manifest'])
            values = {
                'manifests_commands': commands,
                'call_functions': '\n'.join(call_functions),
                'server': cfg['settings']['address'],
                'port': cfg['settings']['port']
            }
            contents = utils.file_read(template_file)
            contents = utils.apply_template(contents, values, template_file)
            logging.info('%(fqdn)s - bootstrap init file generated' % pxe_vars)
        else:
            raise Exception('%(fqdn)s - generating bootstrap init file failed'
                % pxe_vars)
        return contents
     
    def write_status(self, state, pxe_vars):
        """write a file with custom status"""
        logging.info('setting state to "%s"', state)
        file_name = '%s_%s.state' % (pxe_vars['fqdn'], state)
        file_name = os.path.join(cfg['paths']['status'], file_name)
        utils.file_write(file_name, state)

    def net(self, query):
        """this function gets called by the installer and will write to log"""
        #FIXME: add host
        parse.parse_net(query)
        logging.info('enabled host')

    def file(self, query, selection):
        """internal web/file server"""
        if not 'file' in query:
            raise Exception('the file query string is missing')

        file_name = query['file'][0]
        file_name = os.path.basename(file_name)
        file_name = os.path.join(cfg['paths'][selection], file_name)
        self.info = 'requesting file "%s"' % file_name
        contents = utils.file_read(file_name)
        return contents


class GetHandler(BaseHTTPRequestHandler):
    """override BaseHTTPRequestHandler"""

    def log_message(self, format, *args):
        """add logging"""
        sys.stderr.write('%s - - [%s] %s\n' % (self.address_string(),
            self.log_date_time_string(), format%args))
        logging.info('%s - %s' % (self.address_string(), format%args))

    def read_pxe_variables(self, pxe_file):
        """read all seedbank variables from the pxe file"""
        data = utils.file_read(pxe_file)
        data = re.search(
            r'# \*\*\* start - seedBank pxe variables \*\*\*$(.*?)\*\*\*',
            data, re.M|re.S)
        data = data.group(1).strip()
        #data = re.sub(re.compile('^#', re.MULTILINE), '', data)
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
        lines = dict(lines)
        return dict(lines)

    def do_GET(self):
        """process the url path and take action"""
        parsed_path = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(parsed_path.query)

        # security fix
        for key in query:
            values = [os.path.basename(value) for value in query[key]]
            query[key] = values

        paths = parsed_path.path[1:].split('/')
        selection = paths.pop(0)

        require_address = ['seed', 'overlay.tgz', 'bootstrapinit', 'disable',
            'pimp', 'status']
        if 'address' in query:
            address = query['address'][0]
            pxe_file = os.path.join(cfg['paths']['tftpboot'], 'pxelinux.cfg',
                address)
            #if not os.path.isfile(pxe_file):
            #    pxe_file = pxe_file + '.disabled'
            if not os.path.isfile(pxe_file):
                raise Exception('"%s" does not exist' % pxe_file)
            else:
                pxe_vars = self.read_pxe_variables(pxe_file)
        elif selection in require_address:
            raise Exception('"%s" requires an address in the querystring' %
                selection)

        contents = ''
        process = ProcessRequest()
        try:
            if selection == 'pimp':
                logging.info('%(fqdn)s - installation started', pxe_vars)
            elif selection == 'net':
                contents = process.net(query)
            elif selection == 'seed':
                template_cfg = settings.template(pxe_vars['fqdn'],
                    pxe_vars['overlay'], pxe_vars['config'], pxe_vars)
                seed = pimp.SeedPimp(template_cfg, 'net')
                contents = seed.pimp(pxe_vars['seeds'], pxe_vars['overlay'],
                    pxe_vars['manifests'])
            elif selection == 'recipes':
                contents = process.file(query, selection)
            elif selection == 'manifests.tgz':
                contents = utils.tar_gz_directory(cfg['paths']['manifests'])
            elif selection == 'overlay.tgz':
                overlay = pimp.Overlay(cfg, pxe_vars['overlay'], pxe_vars['fqdn'])
                overlay.prepare(pxe_vars)
                permissions = pimp.OverlayPermissions(cfg)
                permissions.script(overlay.dst, pxe_vars['overlay'], '/target')
                contents = utils.tar_gz_directory(overlay.dst)
            elif selection == 'bootstrapinit':
                contents = process.bootstrapinit(pxe_vars)
            elif selection == 'disable':
                utils.file_move(pxe_file, pxe_file + '.disabled')
                if cfg['hooks']['disable']:
                    for cmd in cfg['hooks']['disable']:
                        utils.run(cmd)
            elif selection == 'logging':
                logging.info(query['message'][0])
            elif selection == 'status':
                process.write_status(
                    self.address_string(), query['state'][0], pxe_vars)
            elif selection == 'files':
                process.file(query, selection)
            else:
                raise Exception('"%s" is an unknown request' % selection)
        except utils.FatalException as err:
            logging.error(err)
            self.send_response(404)
            self.wfile.write(err)
        except Exception as err:
            logging.exception(err)
            self.send_response(404)
            self.wfile.write(err)
        else:
            if not contents:
                contents = 'seedBank'
            self.send_response(200)
            self.end_headers()
            self.wfile.write(contents)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """override ThreadedHTTPServer so it will run multithreaded"""


def start():
    logging.info('%(address)s:%(port)s - starting the multithreaded seedBank '
        'daemon', cfg['settings'])
    httpd = ThreadedHTTPServer((cfg['settings']['listen'],
        int(cfg['settings']['port'])), GetHandler)

    try:
        httpd.serve_forever()
    except SystemExit as err:
        sys.exit(err.code)
    except KeyboardInterrupt:
        logging.info('stopped the seedBank daemon')
        sys.stderr.write('info: cancelled by user\n')
        sys.exit()
