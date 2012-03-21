#!/usr/bin/env python

"""this module is shared by the Infrastructure Anywhere and seedBank project"""

# Copyright 2011-2012 Jasper Poppe <jpoppe@ebay.com>
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
__copyright__ = 'Copyright (c) 2011-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '2.0.0rc4'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'development'

import argparse
import cStringIO
import datetime
import json
import logging
import os
import pprint
import shutil
import socket
import string
import subprocess
import sys
import tarfile
import urllib
import urllib2
import yaml


class FatalException(Exception):

    def __init__(self, *args):
        """if an error message has been defined log it to the logging debug
        level"""
        if args:
            self.msg = args[0]
            logging.debug(self.msg)
            sys.exit(1)
        else:
            self.msg = ''
            sys.exit(1)

    def __str__(self):
        """return error message as a string"""
        return repr(self.msg)


def json_client(url, data):
    """send a python dictionary as json to a rest api"""
    request = urllib2.Request(url, data=json.dumps(data),
        headers={'Content-Type': 'application/json'})
    try:
        response = urllib2.urlopen(request).read()
        if response:
            logging.info(response)
    except urllib2.URLError as err:
        logging.error('failed to connect to "%s"', url)
        raise FatalException(err)

def resolve_ip_address(name):
    """resolve a host ip address by host name"""
    try:
        address = socket.gethostbyname(name)
    except socket.error as err:
        logging.error('%s - failed to resolve IP address', name)
        raise FatalException(err)
    else:
        return address

def date_time():
    """return the current date as a string example output: 2012-02-16 14:18"""
    now = datetime.datetime.now()
    result = now.strftime("%Y-%m-%d %H:%M")
    return result

def fqdn_split(fqdn):
    """split a fully qualified domain and return the host name and dns domain,
    when no domain has been specified an empty string will be returned as 
    dns domain"""
    split_host = fqdn.split('.')
    if len(split_host) == 1:
        host_name = split_host[0]
        dns_domain = ''
    else:
        host_name = split_host.pop(0)
        dns_domain = '.'.join(split_host)
    return host_name, dns_domain

def defaults_add(dictionary, defaults):
    """if a value has not been defined in the dictionary add it from defaults"""
    if dictionary:
        for key in defaults.keys():
            if not key in dictionary.keys():
                dictionary[key] = defaults[key]
        return dictionary
    else:
        return defaults

def defaults_override(dictionary, overrides):
    """override and append values from defaults to dictionary"""
    for key in overrides:
        dictionary[key] = overrides[key]
    return dictionary

def _shell_escape(command):
    """escape quotes, backticks and dollar signs"""
    for char in ('"', '$', '`'):
        command = command.replace(char, '\%s' % char)
    return command

def run_old(command, user=None, host=None):
    """run a local or remote command via SSH"""
    if user and host:
        command = _shell_escape(command)
        proc = subprocess.Popen(['ssh', '-o PasswordAuthentication=no', '%s@%s'
            % (user, host), 'bash -c "%s"' % command], stdout=subprocess.PIPE)
    else:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        logging.info('running "%s"', command)
    return proc.stdout.read()

def run(command, user=None, host=None):
    """run a command locally or remote via SSH"""
    if host != 'localhost' and user and host:
        logging.info('%s@%s - running "%s"', user, host, command)
        command = _shell_escape(command)
        proc = subprocess.Popen(['ssh', '-t', '-o PasswordAuthentication=no',
            '%s@%s' % (user, host),
            'bash -c "%s"' % command], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=sys.stdin)
    else:
        logging.info('localhost - running "%s"', command)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    #return_code = proc.Poll()
    #print(return_code)
    #if stderr:
    #    logging.info(stderr)
    return stdout
    #return proc.stdout.read()

def call(command, user=None, host=None):
    """run a local or remote command via SSH"""
    if user and host:
        command = _shell_escape(command)
        #command = 'ssh %s@%s-noproxy "bash -c \'%s\'"' % (user, host, command)
        #subprocess.call(['ssh', '%s@%s-noproxy' % (user, host), 'bash -c "%s"'
        #    % command])
        return_code = subprocess.call(['ssh', '-o PasswordAuthentication=no',
            '%s@%s' % (user, host), 'bash -c "%s"' % command],
            stdout=subprocess.PIPE)
    else:
        return_code = subprocess.call(command, stdout=subprocess.PIPE)
        #subprocess.call(command)
    return return_code

def input_yes_no(question):
    """return True/False on yes/no"""
    yes = set(['yes', 'ye', 'y'])
    no = set(['no', 'n', ''])

    sys.stdout.write(question + ' [y/N]: ')
    choice = raw_input().lower()
    if choice in yes:
       return True
    elif choice in no:
       return False
    else:
        print('error: please respond with "yes" or "no"')
        input_yes_no(question)

def put(src, dst, user=None, host=None):
    """scp a file or directory"""
    command = ['scp', '-r', src, dst]
    subprocess.Popen(command, stdout=subprocess.PIPE)

def yaml_read(files):
    """read one or multiple YAML file(s) return a Python dictionary"""
    if not type(files) == list:
        files = [files]
    try:
        result = yaml.load(files_read(files))
    except Exception as err:
        logging.error('failed to parse "%s"', ', '.join(files))
        logging.error(err)
        raise FatalException()
    else:
        return result

def yaml_from_dict(dictionary):
    """convert a Python dictionary to YAML"""
    return yaml.dump(dictionary)

def file_read(file_name):
    """return the contents of a file"""
    try:
        result = open(file_name, 'r').read()
    except IOError as err:
        logging.error('failed to read "%s"', file_name)
        raise FatalException(err)
    else:
        return result

def files_read(file_names):
    """merge contents of all the files in the list and return it"""
    result = [file_read(file_name) for file_name in file_names]
    return ''.join(result)

def file_write(file_name, data):
    """write data to a file"""
    try:
        open(file_name, 'w').write(data)
    except IOError as err:
        logging.error('failed to write data to "%s" (%s)', file_name, err[1])
        raise FatalException()
    else:
        logging.info('written data to "%s"', file_name)

def file_copy(src, dst):
    """copy a file with metadata"""
    try:
        shutil.copy2(src, dst)
    except (IOError, OSError) as err:
        logging.error('failed to copy "%s" to "%s"', src, dst)
        raise FatalException(err)
    else:
        logging.info('copied "%s" to "%s"', src, dst)

def file_move(src, dst):
    """move a file"""
    try:
        shutil.move(src, dst)
    except (IOError, OSError) as err:
        logging.error('failed to move "%s" to "%s"', src, dst)
        raise FatalException(err)
    else:
        logging.info('moved "%s" to "%s"', src, dst)

def file_delete(path):
    """delete a file"""
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as err:
            logging.error('failed to delete "%s"', path)
            raise FatalException(err)
        else:
            logging.info('deleted "%s"' % path)
            return True

def file_list(path, extension):
    """list file(s) in a directory and strip the given extension"""
    try:
        for name in os.listdir(path):
            if os.path.isfile(os.path.join(path, name)):
                if extension in name:
                    print(name.rsplit(extension, 1)[0])
    except OSError as err:
        logging.error('failed to get contents of directory "%s"', path)
        raise FatalException(err)

def dir_list(path):
    """return a list with all directory names in the given path"""
    result = []
    try:
        for name in os.listdir(path):
            if os.path.isdir(os.path.join(path, name)):
                result.append(name)
    except OSError as err:
        logging.error('failed to get contents of directory "%s"', path)
        raise FatalException(err)
    else:
        return result

def copy_tree(src, dst):
    """copy a directory"""
    try:
        shutil.copytree(src, dst)
    except (IOError, OSError) as err:
        logging.error('failed to copy directory "%s" to "%s"', src, dst)
        raise FatalException(err)
    else:
        logging.info('copied directory "%s" to "%s"', src, dst)

def make_dirs(path):
    """create a recursive path"""
    if os.path.isdir(path):
        return

    try:
        os.makedirs(path)
    except (OSError, IOError) as err:
        logging.error('failed to create directory "%s"', path)
        raise FatalException(err)
    else:
        logging.info('created directory "%s"', path)

def chmod(path, perms):
    """change perms for a file or directory"""
    try:
        os.chmod(path, perms)
    except IOError as err:
        logging.error('changing permissions "%s" to "%s" failed', path, perms)
        raise FatalException(err)
    else:
        logging.info('changed permissons "%s" to "%s"', path, perms)

def apply_template(data, values, log=None):
    """apply a template to a string"""
    try:
        data = string.Template(data)
        data = data.substitute(values)
    except KeyError as err:
        if log:
            logging.error('processing template variables failed, could not '
                'find value for key %s (%s)', err, log)
        else:
            logging.error('processing template variables failed, could not '
                'find value for key %s', err)
        raise FatalException(err)
    else:
        return data

def write_template(values, src, dst=None):
    """open a template file, apply template variables, write to a new file"""
    if not dst:
        dst = src
    data = file_read(src)
    contents = apply_template(data, values, src)
    file_write(dst, contents)

def rmtree(path):
    """delete a directory an the contents"""
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except (IOError, OSError) as err:
            logging.error('failed to remove %s"', path)
            raise FatalException(err)
        else:
            logging.info('removed directory "%s"', path)
            return True

def read_url(url):
    """return the contents of a url as a string"""
    try:
        result = urllib.urlopen(url).readlines()
    except Exception as err:
        logging.error('failed to read "%s"', url)
        raise FatalException(err)
    else:
        return result

def _reporthook(count, block_size, total_size):
    """download hook for showing progress"""
    mb = float(total_size) / 1024 / 1024
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write('\rinfo: progress %3.1f%% of %.2fMB' % (percent, mb))
    sys.stdout.flush()

def download(url, dst, report_hook=False):
    """download a file"""
    logging.info('downloading "%s" to "%s"', url, dst)
    try:
        (filename, headers) = urllib.urlretrieve(url, dst, report_hook)
    except Exception as err:
        logging.error('failed to download "%s"' % url)
        raise FatalException(err)
    else:
        logging.info('finished downloading "%s"', url)

def recursive(path, define, arg):
    for root, _, files in os.walk(path):
        define(root, arg)
        for file_name in files:
            define(os.path.join(root, file_name), arg)

def initrd_extract(path, initrd):
    """extract an initrd image"""
    if sys.platform == 'darwin':
        cpio = 'gnucpio'
    else:
        cpio = 'cpio'
    run('cd "%s" && gzip -d < "%s" | %s --extract --make-directories ' 
        '--no-absolute-filenames' % (path, initrd, cpio))

def initrd_create(path, initrd):
    """create an initrd image"""
    if sys.platform == 'darwin':
        cpio = 'gnucpio'
    else:
        cpio = 'cpio'
    run('cd "%s" && find . | %s -H newc --create | gzip -1 > "%s"' %
        (path, cpio, initrd))

def tar_gz_directory(path):
    """tar and gzip a path, return a tgz file"""
    current_cwd = os.getcwd()
    os.chdir(path)
    try:
        tar_file = cStringIO.StringIO()
        tar = tarfile.open(fileobj=tar_file, mode='w:gz')
        tar.add('.')
        tar.close()
        os.chdir(current_cwd)
    except Exception as err:
        logging.error('creating gzipped tar archive of "%s" failed', path)
        raise FatalException(err)
    else:
        logging.info('created gzipped tar archive of "%s"', path)
        return tar_file.getvalue()

def untar(archive, dst):
    """extract all files from a gzipped tarball"""
    try:
        tar = tarfile.open(archive, 'r:gz')
        tar.extractall(dst)
        tar.close()
    except IOError as err:
        logging.error('failed to extract "%s" to "%s"', archive, dst)
        raise FatalException(err)
    else:
        logging.info('extracted files to "%s"', dst)

def untar_files(archive, files, dst):
    """untar selected files from a gzipped tarball"""
    try:
        os.chdir(dst)
        tar = tarfile.open(archive, 'r:gz')
        tar.extractall('', members=(tar.getmember(member) for member in files))
        tar.close()
    except IOError as err:
        logging.error('failed to extract "%s" to "%s"', archive, dst)
        raise FatalException(err)
    else:
        logging.info('extracted "%s" to "%s"', archive, dst)

def ip_to_hex(address):
    """return a ipv4 address to hexidecimal"""
    return ''.join(['%02X' % int(octet) for octet in address.split('.')])

def format_address(address):
    """return and format a mac or ip address"""
    if '.' in address:
        address = ip_to_hex(address)
    else:
        address = address.replace(':', '-')
        address = address.lower()
        if not '-' in address:
            address = '-'.join([''.join(octet)
                for octet in zip(*[list(address[part::2])
                    for part in range(2)])])
        if len(address) != 20:
            address = '01-' + address
    return address

################################################################################
# unused defines
################################################################################

def validate_ip(ip_address):
    """check if ip address is valid"""
    try:
        socket.inet_aton(ip_address)
    except socket.error as err:
        logging.error(err)
        raise FatalException(err)
    else:
        return True

def resolve_host_name(name):
    """resolve host name for a host by IP address"""
    try:
        host_name = socket.gethostbyaddr(name)[0]
    except socket.error as err:
        logging.error('%s - failed to resolve IP address', name)
        raise FatalException(err)
    else:
        return host_name

def resolve_fqdn(name):
    """resolve fully qualified domain name by host name"""
    try:
        fqdn = socket.getfqdn(name)
    except socket.error as err:
        logging.error('%s - failed to resolve fully qualified domain name',
            name)
        raise FatalException(err)
    else:
        return fqdn

'''
def host_by_ip(address):
    try:
        socket.inet_aton(address)
    except socket.error as err:
        logging.error(err)
        raise FatalException(err)
'''
################################################################################

def main():
    """used for testing the utils"""
    parser = argparse.ArgumentParser(description='utils')
    parser.add_argument('--download', nargs=2)
    parser.add_argument('--dumpyaml', nargs=2)
    '''
    parser.add_argument('--download', action='store_true')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
        const=sum, default=max,
        help='sum the integers (default: find the max)')
    '''
    args = parser.parse_args()

    if args.download:
        url, dst = args.download
        print(url, dst)
        download(url, dst)
    elif args.dumpyaml:
        pprint.pprint(yaml_read(args.dumpyaml))

    #print(args.accumulate(args.integers))

if __name__ == '__main__':
    main()
