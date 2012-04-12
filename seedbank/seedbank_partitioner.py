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

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2009-2012 Jasper Poppe'
__credits__ = ''
__license__ = 'Apache License 2.0'
__version__ = '2.0.0rc6'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jpoppe@ebay.com'
__status__ = 'production'

import optparse
import os
import subprocess
import sys


class ProcessInput:

    def __init__(self):
        self.devices = {}
        self.valid_options = []
        self.valid_fstypes= []

    def read_recipe(self, filename):
        data = open(filename).readlines()

        for line in data:
            if line:
                line = line.strip()
                if line.startswith('device'):
                    device = line.split(' ')[1]
                    if self.devices.has_key(device):
                        print ('error: device "%s" is a duplicate' % device)
                        sys.exit(1)
                    self.devices[device] = {}
                    self.devices[device]['partition'] = []
                elif line.startswith('options'):
                    options = line.split(' ', 1)[1]
                    options = options.split(';')
                    options = [option.strip() for option in options]
                    self.devices[device]['options'] = options
                elif line.startswith('partition'):
                    line = line.split(' ', 1)[1]
                    values = line.split(';')
                    values = [value.strip() for value in values]
                    values = [value.split('=') for value in values]
                    self.devices[device]['partition'].append(dict(values))

        return self.devices

    def parser(self):
        for device in self.devices:
            self.sanity_device(device, self.devices[device])
            self.sanity_options(device, self.devices[device])
            self.sanity_partition(device, self.devices[device])

        return self.devices

    def sanity_device(self, device, data):
        device = os.path.join('/sys/block', device)
        if not os.path.isdir(device):
            print ('error: block device "%s" not found' % device)
            sys.exit(1)

    def sanity_options(self, device, data):
        for option in data['options']:
            if not option in self.valid_options:
                print ('error: option "%s" for device "%s" is not a valid option' % (option, device))
                sys.exit(1)

    def sanity_partition(self, device, data):
        for partition in data['partition']:
            required = ['size', 'mount', 'fstype', 'fsoptions']
            for key, value in partition.items():
                if not key in required:
                    print ('error: option "%s" for device "%s" is not a valid option' % (key, device))
                    sys.exit(1)
                else:
                    required.remove(key)
            
                if key == 'fstype':
                    self.sanity_fstype(device, value)
                elif key == 'size':
                    size = self.sanity_size(device, value)
                    partition['size'] = size
                elif key == 'fsoptions':
                    #size = self.sanity_options(device, value)
                    partition['fsoptions'] = value
                elif key == 'mount':
                    if not value.startswith('/'):
                        print ('error: option "%s" for device "%s" is not a valid mountpoint' % (key, device))
                        sys.exit(1)

            if required:
                print ('error: mandatory option(s) "%s" for device "%s" is/are not set' % (required, device))
                sys.exit(1)


    def sanity_fstype(self, device, fstype):
        if not fstype in self.valid_fstypes:
            print ('error: "%s" for device "%s" is not a valid file system' % (fstype, device))

    def sanity_size(self, device, size):

        units = {
            'KB': 1000,
            'MB': 1000 ** 2,
            'GB': 1000 ** 3,
            'TB': 1000 ** 4,
            'KiB': 1024,
            'MiB': 1024 ** 2,
            'GiB': 1024 ** 3,
            'TiB': 1024 ** 4,
        }

        for key in units:
            if key in size:
                size = size.replace(key, '')
                break

        try:
            if not size == 'grow':
                byte_size = (int(units[key]) * int(size))
            else:
                byte_size = 'grow'
        except:
            print ('error: "%s" for device "%s" is not a valid size unit' % (size, device))
        else:
            return byte_size

class Partitioner:

    def __init__(self, recipe):
        self.sector = 0
        self.recipe = recipe
        self.script = []

    def align(self):
        pass

    def growsize(self):
        for device in self.recipe:
            disk_size = run(['/sbin/sfdisk','-s', '/dev/%s' % 'sda']).strip()
            disk_size = int(disk_size) * 1024

            disk_size_used = sum([partition['size']
                                    for partition in self.recipe[device]['partition']
                                        if partition['size'] != 'grow'])
            partition_size_grow = disk_size - disk_size_used - 512 * 8192 # Compensate for 4MB worth of sectors at end of disk

            for partition in self.recipe[device]['partition']:
                if partition['size'] == 'grow' and 'rootdisk' not in self.recipe[device]['options']:
                    partition['size'] = partition_size_grow # Roel

    def gensfdisk(self):
        sector_current = 0

        for device in self.recipe:
            if 'rootdisk' not in self.recipe[device]['options']: 
                self.script.append('sfdisk -f -uS /dev/%s << EOS' % device)
                for partition in self.recipe[device]['partition']:
                    if 'align' in self.recipe[device]['options']:
                        sector_current += (128 - sector_current % 128)

	                self.script.append('%s,%s,L' % (sector_current, partition['size']/512))

                    sector_current += (partition['size']/512 + 1)
                self.script.append('EOS')

    def genroot(self):
        for device in self.recipe:
            if 'rootdisk' in self.recipe[device]['options']: 
                self.script.append("d-i partman-auto/method string regular".ljust(70))
                self.script.append(("d-i partman-auto/disk string /dev/%s" % (device)).ljust(70))
                self.script.append("d-i partman-auto/expert_recipe string".ljust(70) + "\\")
                self.script.append("      boot-root ::".ljust(70) + "\\")
                partition_current = 1
                for partition in self.recipe[device]['partition']:
                    if partition['size'] == 'grow':
                        self.script.append(("              1 1 100000000 %s" % (partition['fstype'])).ljust(70) + "\\")
                    else:
                        size_mb = "%d" % round(int(partition['size'])/1024/1024)
                        self.script.append(("              %s %s %s %s" % (size_mb, size_mb, size_mb, partition['fstype'])).ljust(70) + "\\")

                    if partition['fstype'] == 'swap':
                        self.script.append("                      method{ swap } format{ }".ljust(70) + "\\")
                    else:
                        self.script.append("                      method{ format } format{ }".ljust(70) + "\\")
                        self.script.append(("                      use_filesystem{ } filesystem{ %s }" % partition['fstype']).ljust(70) + "\\")
                        self.script.append(("                      mountpoint{ %s }" % partition['mount']).ljust(70) + "\\")

                    if partition_current == 1:
                        self.script.append("                      $primary{ } $bootable{ }".ljust(70) + "\\") 

                    self.script.append("              .".ljust(70) + "\\") 

                    partition_current += 1


    def filesystem(self):
        for device in self.recipe:
            if not 'rootdisk' in self.recipe[device]['options']:
                partition_current = 1
                for partition in self.recipe[device]['partition']:
                    target = '/dev/%s%s' % (device, partition_current)
                    self.script.append('mkfs.%s %s' % (partition['fstype'], target))
                    self.script.append('tune2fs -L %s %s' % (target, target))
                    self.script.append('UUID=$(blkid -o value -s UUID %s)' % target)
                    self.script.append('echo "UUID=$UUID %(mount)s %(fstype)s %(fsoptions)s 0 0" >> /etc/fstab' % partition)
                    self.script.append('mkdir -p %(mount)s' % partition)
                    partition_current += 1

                self.script.append('mount -a\n')


def run(command):
    """run an external command, return output"""
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, err = p.communicate()
    return output

def generate(filename):
    process = ProcessInput()
    process.valid_options = ['align', 'force', 'rootdisk']
    process.valid_fstypes = ['ext2', 'ext3', 'ext4', 'xfs', 'swap']
    process.read_recipe(filename)
    xpart = Partitioner(process.parser())
    xpart.growsize()
    xpart.gensfdisk()
    xpart.filesystem()
    return '\n'.join(xpart.script)

def main():
    """main application, this function won't called when used as a module"""
    parser = optparse.OptionParser(prog='seedbank_daemon', version=__version__)
    parser.set_description ('seedbank partitioner (c) 2009, 2010, 2011 Jasper Poppe <jpoppe@ebay.com>')
    parser.set_usage('%prog [-d|-r] <recipe>')
    parser.add_option('-d', dest='dry', help='dry run (print partition script to screen)', action='store_true')
    parser.add_option('-r', dest='run', help='run (print partition script to screen)', action='store_true')
    (opts, args) = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit()
    elif len(args) != 1:
        parser.error('the seedbank partitioner takes exactly one argument')

    if not os.path.isfile(args[0]):
        parser.exit('error: "%s" is not a valid file' % args[0])

    if opts.dry and opts.run:
        parser.error('you can not use option dry and run together')

    partition_script = generate(args[0])
    if opts.dry:
        print (partition_script)
    else:
        script = '/tmp/seedbank_partitioner.sh'
        print ('info: writing generated partitioner script "%s"' % script)
        try:
            file = open(script, 'w')
        except:
            parser.error('can not open file "%s" for writing' % script)
        else:
            file.write(partition_script)
            file.close()

    if opts.run:
        print ('info: running partitioner script "%s"' % script)
        run(['sh', script])
        
if __name__ == '__main__':
    main()
