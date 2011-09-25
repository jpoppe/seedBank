# Copyright 2011, Jasper Poppe <jpoppe@ebay.com>, Lex van Roon
# <lvanroon@ebay.com>
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

from __future__ import with_statement
from fabric.api import local, env, run, settings
from fabric.contrib import console
from factory import libvirt, chicken, powerdns_fabric
from fabric.colors import magenta

import ast
import os
import re
import sys
import time

if not env['hosts']:
    env['hosts'] = ['localhost']
    connect = 'qemu:///system'
elif len(env['hosts']) > 1:
    print ('error: this script works only with 1 host at the same time')
    sys.exit(1)
else:
    connect = 'qemu+ssh://root@%s/system' % env['hosts'][0]

defaults = {
    'confirm': False,                          # Confirm the steps to be made
    'connect': connect,                       # Libvirt instance to connect to
    'dns_domain': 'a.c.m.e',
    'seedbank': '192.168.122.2',
    'ram': '256',                             # Amount of ram to allocate to vm
    'vcpus': '1',                             # Number of CPU's to allocate to vm
    'cpu_type': 'Nehalem',                    # CPU type to use
    'disk_size': '3',                         # Amount of diskspace to allocate, in GB
    'home_dir': os.path.expanduser('~'),      # Home directory
    'os_type': 'linux',                       # OS type to use
    'os_variant': 'debiansqueeze',            # OS variant to use
    'storage_dir': '/var/lib/libvirt/images', # Where the storage pools are located
    'storage_pool': 'acmefactory',            # The name of the storage pool to use
    'storage_owner': 'libvirt-qemu',          # The owner of the storage pool
    'storage_mode': '0770',                   # Permissions for the storage pool
    'storage_type': 'qcow2',                  # can be qcow2 or lvm
    'storage': 'default',                     # name of the (remote) storage pool
    'volumegroup': 'acmefactory',             # set to name of the lvm volume group
    'git_dir': os.path.expanduser('~/git'),   # Where the local git repository is
    'work_dir': '/tmp/chicken',               # What to use as a working directory
    'git_target': '/tmp/chicken/acmefactory',
    'work_dir_local': '/tmp/chicken/local',   # What to use as a working directory
    'work_dir_remote': '/tmp/chicken/remote', # What to use as a working directory
    'git_repo': 'ecg-puppet-staging',         # which repository to use
    'iso_url': 'http://cdimage.debian.org/debian-cd/current/amd64/iso-cd',
    'repository': '192.168.122.1',
    'ext_net': 'default',                     # name of the external bridge
    'int_net': 'internal',                    # name of the internal bridge
    'ssh': '/usr/bin/ssh',                    # Path to (custom) ssh
    'overlord': ['192.168.122.2'],
    'platform_type': 'libvirt'                # Backend to use, only 'libvirt' is supported for now
}

for key in defaults.keys():
    if not key in env.keys():
        env[key] = defaults[key]

if not isinstance(env['overlord'], list):
    env['overlord'] = ast.literal_eval(env['overlord'])

if env['platform_type'] == 'libvirt':
    backend = libvirt
else:
    print ("%s is not a supported backend" % env['platform_type'])
    sys.exit(1)

chicken.env = env

def _overlord(name, ip_address, ip_address2, overlay='overlord', auto='False', repository='192.168.122.1', puppet=True, snapshot='false'):
    virtual = env
    virtual['name'] = name
    virtual['fqdn'] = '%s.%s' % (name, env['dns_domain'])
    virtual['mac'] = backend.ip_to_mac(ip_address)
    virtual['mac2'] = backend.ip_to_mac(ip_address2)
    virtual['ram'] = '2048'
    virtual['vcpus'] = '2'
    virtual['disk_size'] = '4'
    virtual['ip_address'] = ip_address
    virtual['ip_address2'] = ip_address2
    virtual['cpus'] = '2'
    virtual['cdrom'] = '%(name)s.iso' % virtual
    virtual['home_dir'] = env['home_dir']
    virtual['overlord'] = env['overlord'][0]

    if defaults['confirm'] and not console.confirm('Removing the "%(overlord)s" SSH known hosts entry. Do you want to continue?' % virtual):
        sys.exit(0)

    print(magenta('Removing the SSH known_hosts entries for "%(overlord)s"' % virtual, True))
    local('ssh-keygen -f %(home_dir)s/.ssh/known_hosts -R %(overlord)s' % virtual)
    local('ssh-keygen -f %(home_dir)s/.ssh/known_hosts -R %(name)s' % virtual)

    if env['platform_type'] == 'libvirt':
        if not backend.has_pool(virtual['storage_pool']):
            backend.create_pool(virtual['storage_pool'])
    
        if defaults['confirm'] and not console.confirm('Breeding the egg (ISO). Do you want to continue?' % virtual):
            sys.exit(0)

        print(magenta('Creating the ISO', True))
        chicken.breed(name, ip_address, puppet, overlay)
        backend.refresh_pool(virtual['storage_pool'])

    if defaults['confirm'] and not console.confirm('Start the virtual machine?' % virtual):
        sys.exit(0)

    print(magenta('Starting the virtual machine.', True))
    backend.create('server', virtual)
    if env['platform_type'] == 'libvirt':
        virt_connect(virtual['name'], 'overlord')

def _minion(name, ip_address, domain='a.c.m.e', ram='512', disk_size='3', type='debian-squeeze-amd64', overlay='minion'):
    virtual = env
    virtual['name'] = name
    virtual['fqdn'] = '%s.%s' % (name, env['dns_domain'])
    virtual['mac'] = backend.ip_to_mac(ip_address)
    virtual['ram'] = ram
    local('ssh-keygen -f "%s/.ssh/known_hosts" -R %s' % (os.path.expanduser('~'), ip_address))
    local('ssh-keygen -f "%s/.ssh/known_hosts" -R %s' % (os.path.expanduser('~'), name))
    with settings(host_string=env['seedbank'], user='root'):
        powerdns_fabric.add_host(name, env['mac'], ip_address)
        run('seedbank -M %s -r one-partition -s squeeze -o %s %s.%s %s' % (env['mac'], overlay, name, env['dns_domain'], type))

    backend.create('client', virtual)
    if env['platform_type'] == 'libvirt':
        virt_connect(virtual['name'], 'minion')

################################################################################################

def sync(name='overlord001', destination='/etc/puppet'):
    env['name'] = name
    env['destination'] = destination
    env['remote_user'] = 'root'
    local('rsync -e %(ssh)s -av --delete --no-o --no-g %(git_dir)s/%(git_repo)s/* %(remote_user)s@%(name)s:%(destination)s' % env)

def test(name='overlord001', debug=False):
    for overlord in env['overlord']:
        sync(overlord)
    with settings(host_string=name, user='root'):
        if debug:
            run('puppet agent -t --debug || true')
        else:
            run('puppet agent -t || true')

def check(name='overlord001'):
    with settings(host_string=name, user='root'):
        run('cat /var/log/bootstrap_puppet.log | egrep \'warning: |err: \'; true')

def test_bootstrap(name='overlord001'):
    sync(name, destination='/root/%(git_repo)s' % env)
    with settings(host_string=name, user='root'):
        run('bash /usr/local/bin/puppet_bootstrap')

def bootstrap(name='overlord001'):
    env['name'] = name
    local('cd %(git_dir)s && tar cf - %(git_repo)s | ssh %(name)s "tar xf - -C /root"' % env)
    local('ssh %(name)s "puppet_bootstrap"' % env)

################################################################################################

def list_all_snapshots():
    all_snapshots = {}
    nodes = backend.list_nodes()
    for node in nodes:
        all_snapshots[node] = backend.list_snapshots(node)

    print ('Node%sName%sDate' % (' ' * 31, ' ' * 11))
    print ('-' * 75)
    for node, snapshots in all_snapshots.items():
        for name, date in all_snapshots[node].items():
            print('%s%s%s' % (node.ljust(35), str(name).ljust(15), date))

def list_snapshots(name):
    snapshots = backend.list_snapshots(name)
    print ('Snapshot            Created on')
    print ('-' * 45)
    for name, date in snapshots.items():
        print ('%s%s' % (str(name).ljust(20), date))

def create_snapshot(name='overlord001'):
    local('kvm-img snapshot -c virgin /var/lib/libvirt/images/acmefactory/%s.img' % name)
    #backend.create_snapshot(name)

def restore_snapshot(name, snapshot):
    if backend.has_snapshot(name, snapshot):
        backend.restore_snapshot(name, snapshot)

def remove_snapshot(name, snapshot):
    if backend.has_snapshot(name, snapshot):
        backend.remove_snapshot(name, snapshot)

def update_dns_domain():
    powerdns_fabric.update_dns_domain()

################################################################################################

def remove(name):
    re_remove = re.compile(name, re.I)
    for node in backend.list_nodes():
        if re_remove.search(node):
            backend.remove(node)

def remove_all():
    remove('.*')

def test_chicken():
    chicken.clean(overlord001)
    chicken.extract_iso()

################################################################################################

def virt_connect(name, script):
    """Hack because libvirt doesn't allow to start machine after an installation"""
    local('/bin/bash -c "sleep 20; nohup ./start_vm.sh %s.a.c.m.e >& /dev/null < /dev/null" &' % (name))
    local('/bin/bash -c "sleep 20; nohup ./%s.sh %s.a.c.m.e >& /dev/null < /dev/null" &' % (script, name))

################################################################################################

def overlord001(ip_address='192.168.122.2', ip_address2='192.168.20.1', central_ca=False, puppet=True):
    env['extdata_file'] = '%s.csv' % ('-'.join(env['dns_domain'].split('.')[:2]))
    if console.confirm('Do you want to remove all machines in the "%s" domain?' % env['dns_domain']):
        print(magenta('Removing all nodes from the "%s" domain' % env['dns_domain'], True))
        remove('.*.%s' % env['dns_domain'])

    if central_ca:
        overlay='overlord_central_ca'
        local('sed -i "s/puppetca,overlord001.%(dns_domain)s/puppetca,puppetca001.%(dns_domain)s/" %(git_dir)s/%(git_repo)s/modules/xx/platform/xx_base_system/extdata/%(extdata_file)s' % env)
    else:
        overlay='overlord'
        local('sed -i "s/puppetca,puppetca001.%(dns_domain)s/puppetca,overlord001.%(dns_domain)s/" %(git_dir)s/%(git_repo)s/modules/xx/platform/xx_base_system/extdata/%(extdata_file)s' % env)

    _overlord(name='overlord001', ip_address=ip_address, ip_address2=ip_address2, overlay=overlay, puppet=puppet)
    if env['platform_type'] == 'libvirt':
        local('virt-manager')

def overlord002(puppet='True'):
    remove('overlord002.*')
    _overlord(name='overlord002', ip_address='192.168.122.3', ip_address2='192.168.20.2', puppet=puppet)

def minion001(central_ca=False):
    remove('minion001.*')
    if central_ca:
        overlay='minion_cental_ca'
    else:
        overlay='minion'
    _minion(name='minion001', ip_address='192.168.20.101', overlay=overlay)

def minion002(central_ca=False):
    remove('minion002.*')
    if central_ca:
        overlay='minion_cental_ca'
    else:
        overlay='minion'
    _minion(name='minion002', ip_address='192.168.20.102', disk_size='6', overlay=overlay)

def minion003(central_ca=False):
    remove('minion003.*')
    if central_ca:
        overlay='minion_cental_ca'
    else:
        overlay='minion'
    _minion(name='minion003', ip_address='192.168.20.103', disk_size='3', overlay=overlay)

def minion004(central_ca=False):
    remove('minion004.*')
    if central_ca:
        overlay='minion_cental_ca'
    else:
        overlay='minion'
    _minion(name='minion004', ip_address='192.168.20.104', disk_size='3', overlay=overlay)

def puppetca001():
    remove('puppetca001.*')
    _minion(name='puppetca001', ip_address='192.168.20.99', disk_size='3', overlay='puppetca')

def puppetca001_bare():
    remove('puppetca001.*')
    _minion(name='puppetca001', ip_address='192.168.20.99', disk_size='3', overlay='puppetca_bare')

def csinabox():
    _minion(name='csinabox', ip_address='192.168.20.120', ram='1792')

def puppetconf2011():
    overlord001()
    local('while ! nc -w 1 192.168.122.2 7467; do echo "waiting for overlord to finish."; sleep 5; done')
    local('while ! ssh overlord001 ls /var/lib/tftpboot/seedbank/debian-squeeze-amd64/ 2> /dev/null; do echo "waiting for seedbank bootstrap to finish"; sleep 5; done')
    time.sleep(10)
    env['overlord'] = ['192.168.122.2']
    for index in range(1, 5):
        remove('minion00%s.*' % index) 
        _minion(name='minion00%s' % index, ip_address='192.168.20.10%s' % index)
        time.sleep(25)
