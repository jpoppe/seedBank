# Copyright 2009-2015 Jasper Poppe <jgpoppe@gmail.com>
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

import os
import logging

from wsgiref.simple_server import WSGIRequestHandler

from bottle import run, route, request, abort
import bottle

import parse
import pimp
import settings
import utils

cfg = settings.parse_cfg()


class GetHandler(WSGIRequestHandler):
    """override the BaseHTTPRequestHandler used in bottle.py, this only works
    when the (default) WSGIref web server will be used"""
    def log_message(self, format, *args):
        """add logging support"""
        logging.info('%s - %s' % (self.address_string(), format%args))


class AttributeDict(dict): 
    """use attributes to access a dictionary"""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def api_parse(command, args):
    """convert arguments to an object, pass it to parse"""
    if not 'fqdn' in args:
        logging.error('missing mandatory positional argument "fqdn"')
        return

    args = AttributeDict(args)
    parse_arg = parse.ParseArguments(cfg, api=True)
    action = getattr(parse_arg, command)
    try:
        action(args)
    except utils.APIException as err:
        logging.error(err)
        abort(400, err)

@route('/api/:command', method='POST')
def api(command):
    """enable netboot installations or create ISOs via json requests"""
    commands = ('pxe', 'iso')
    if not command in commands:
        abort(404, '"%s" is an invalid command (valid commands: %s)' % (command,
            ', '.join(commands)))
    data = request.json
    if not data:
        abort(400, 'no data received')
    elif not 'args' in data:
        abort(400, 'required key "args" not found in data')
    else:
        api_parse(command, data['args'])

@route('/install/:address')
def install(address):
    """write installation started to the log"""
    pxe_vars = settings.pxe_variables(cfg, address)
    msg = '%(fqdn)s - installation started' % pxe_vars
    logging.info(msg)
    return msg

@route('/seed/:address')
def seed(address):
    """return the generated preseed file"""
    pxe_vars = settings.pxe_variables(cfg, address)
    template_cfg = settings.template(pxe_vars['fqdn'], pxe_vars['overlay'],
        pxe_vars['config'], pxe_vars)
    seed = pimp.SeedPimp(template_cfg, 'pxe')
    try:
        result = seed.pimp(pxe_vars['seeds'], pxe_vars['overlay'],
            pxe_vars['puppet_manifests'])
    except KeyError as err:
        msg = 'key %s not found in the PXE variables' % err
        logging.error(msg)
        abort(400, msg)
    else:
        return result

@route('/puppet_manifests.tgz')
def puppet_manifests():
    """return a gzipped tar archive with all puppet manifests"""
    result = utils.tar_gz_directory(cfg['paths']['puppet_manifests'])
    return result

@route('/overlay.tgz/:address')
def overlay(address):
    """apply templates to a file overlay and return it a gzipped tar archive"""
    pxe_vars = settings.pxe_variables(cfg, address)
    overlay = pimp.Overlay(cfg, pxe_vars['overlay'], pxe_vars['fqdn'])
    overlay.prepare(pxe_vars)
    permissions = pimp.OverlayPermissions(cfg)
    permissions.script(overlay.dst, pxe_vars['overlay'], '/target')
    result = utils.tar_gz_directory(overlay.dst)
    return result

@route('/rclocal/:address')
def rclocal(address):
    """return the rc.local file"""
    pxe_vars = settings.pxe_variables(cfg, address)
    file_name = os.path.join(cfg['paths']['templates'],
        cfg['templates']['rc_local'])
    result = utils.file_read(file_name)
    result = utils.apply_template(result, pxe_vars, file_name)
    return result

@route('/puppet/:manifest')
def puppet(manifest):
    """return the generated seedbank bootstrap init file"""
    file_name = os.path.join(cfg['paths']['templates'],
        cfg['templates']['puppet_manifest'])
    result = utils.file_read(file_name)
    result = utils.apply_template(result, {'manifest': manifest}, file_name)
    return result

@route('/disable/:address')
def disable(address):
    """disable a pxelinux configuration file by renaming the file"""
    file_name = os.path.join(cfg['paths']['tftpboot'], 'pxelinux.cfg', address)
    utils.file_move(file_name, file_name + '.disabled')
    if cfg['hooks_pxe']['disable']:
        for cmd in cfg['hooks_pxe']['disable']:
            utils.run(cmd)

@route('/log/:msg')
def log(msg):
    """write a custom log message to the info level"""
    logging.info(msg)

@route('/status/:address/:msg')
def status(address, msg):
    """write a file with custom status"""
    pxe_vars = settings.pxe_variables(cfg, address)
    logging.info('setting state to "%s"', msg)
    file_name = '%s_%s.state' % (pxe_vars['fqdn'], msg)
    file_name = os.path.join(cfg['paths']['status'], file_name)
    utils.file_write(file_name, msg)

def start():
    """start the bottle daemon"""
    try:
        settings = cfg['settings']
        bottle_server = settings['bottle_server']
        bottle_server = getattr(bottle, bottle_server)
        if not cfg['settings']['bottle_listen']:
            cfg['settings']['bottle_listen'] = '0.0.0.0'
        run(host=cfg['settings']['bottle_listen'],
            port=cfg['settings']['bottle_port'], handler_class=GetHandler,
            server=bottle_server)
    except Exception as error:
        logging.error(error)

if __name__ == 'main':
    start()
