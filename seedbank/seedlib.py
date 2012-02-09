#!/usr/bin/env python

"""

seedBank library

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

This tool downloads the needed netboot tarballs from the internet and
extracts the needed files to the right place, it's also able to integrate
the 'non free' firmware files into the Debian netboot initrd.

"""

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '1.1.0'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import collections
import os
import shutil
import socket
import string
import subprocess
import urllib

def ip_to_hex(address):
    """convert IP address to hex"""
    return ''.join(['%02X' % int(octet) for octet in address.split('.')])

def get_domain(fqdn):
    """split hostname in host and domainname"""
    split_host = fqdn.split('.')
    if len(split_host) == 1:
        hostname = split_host[0]
        domainname = ''
    else:
        hostname = split_host.pop(0)
        domainname = '.'.join(split_host)
    
    return hostname, domainname

def read_file(filename):
    """read contents of a file"""
    try:
        contents = open(filename, 'r').read()
    except IOError:
        print ('error: can not open file %s' % (filename))
    else:
        return contents

def makedirs(path):
    """create directories with parent directories"""
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except IOError:
            print ('error: failed to create "%s"' % path)
        else:
            print ('info: directory "%s" has been created' % path)
    return True

def move(source, destination):
    """rename source to destination"""
    try:
        os.rename(source, destination)
    except IOError:
        print ('error: failed to move "%s" to "%s"' % (source, destination))
    else:
        print ('info: moved "%s" to "%s"' % (source, destination))
        return True

def run(command, out=False):
    """run an external command, print output to screen"""
    Result = collections.namedtuple('Result', 'retcode, error, output')
    try:
        if out:
            child = subprocess.Popen(' '.join(command), shell=True)
        else:
            child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = child.communicate()
        retcode = child.returncode
    except:
        retcode = 3
        error = 'command failed'
        output = ''
    result = Result(retcode, error, output)
    return result

def run_pipe(command):
    """run a pipe command, should be integrated with the run define"""
    Result = collections.namedtuple('Result', 'retcode, error, output')
    child = subprocess.Popen(command, shell=True)
    output, error = child.communicate()
    retcode = child.returncode
    result = Result(retcode, error, output)
    return result

def read_url(url, skip_lines=0):
    """read yaml from an external url"""
    try:
        text = urllib.urlopen(url).readlines()
    except Exception:
        return
    
    for line in range(0, skip_lines):
        del text[0]

    text = ''.join(text)
    return text

def apply_template(data, values):
    """apply template on a string"""
    data = string.Template(data)
    data = data.substitute(values)
    return data

def validate_ip(address):
    """check if ip address is valid"""
    try:
        socket.inet_aton(address)
    except socket.error:
        return
    else:
        return True

def format_address(address):
    """return and format a mac or ip address"""
    if '.' in address:
        address = ip_to_hex(address)
    else:
        address = address.replace(':', '-')
        address = address.lower()
        if not '-' in address:
            address = '-'.join([''.join(x) for x in zip(*[list(address[z::2]) for z in range(2)])])
        if len(address) != 20:
            address = '01-' + address
    return address

def rmtree(dir):
    """delete a directory and all the contents of it"""
    if os.path.isdir(dir):
        try:
            shutil.rmtree(dir)
        except (IOError, OSError):
            print ('error: failed to remove directory "%s"' % dir)
        else:
            print ('info: removed directory "%s"' % dir)
            return True
    else:
        return True


class FormatListDir(object):
    """return a formatted list from a directory"""

    def __init__(self, name):
        """initialize class variables"""
        self.name = name
        self.error = False
        self.entries = ['%s:' % self.name.capitalize()]

    def listdir(self, dir, type, filter=None):
        """liste files or directories in a directory"""
        if not os.path.isdir(dir):
            self.error = 'error: no "%s" found' % self.name
        else:
            if type == 'dirs':
                self.entries += [item for item in os.listdir(dir) if os.path.isdir(os.path.join(dir, item))]
            elif type == 'files':
                self.entries += [item for item in os.listdir(dir) if os.path.isfile(os.path.join(dir, item))]
            else:
                self.entries += [item for item in os.listdir(dir) if os.path.isfile(os.path.join(dir, item))]

            if filter:
                self.entries = [entry for entry in self.entries if not entry.endswith(filter)]

    def rstrip(self, item):
        """strip extension from entries"""
        if not self.error:
            self.entries = [entry.replace(item, '') for entry in self.entries]

    def show(self):
        """if no errors, print the result"""
        if self.error:
            print (self.error)
        else:
            print '\n'.join(self.entries)

def main():
    """main application, this function won't called when used as a module"""
    print ('info: this is the seedbank library, what did you smoke today?!?')

if __name__ == '__main__':
    main()
