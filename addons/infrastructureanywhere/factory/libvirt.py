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

""" libvirt.py (c) 2011 - Jasper Poppe <jpoppe@ebay.com>

    A module to manage libvirt using fabric
"""

from __future__ import with_statement

__author__ = 'Jasper Poppe <jpoppe@ebay.com>'
__copyright__ = 'Copyright (c) 2011 Jasper Poppe'
__credits__ = 'Lex van Roon <lvanroon@ebay.com>'
__license__ = 'copyright'
__version__ = '0.4'
__maintainer__ = ['Jasper Poppe', 'Lex van Roon']
__email__ = 'jpoppe@ebay.com'
__status__ = 'in development'

from fabric.api import local, run, settings, hide, env

import string

def _apply_template(values, template, file_name=None):
    """ Fill a template file with values

        Requires:
        * values -> dict, values to use for substitution
        * template -> string, template to fill
        * file_name -> string, path where to write the result to

        Returns:
        * None
    """
    contents = string.Template(open(template, 'r').read())
    contents = contents.substitute(values)
    if file_name:
        open(file_name, 'w').write(contents)
    else:
        return contents

def ip_to_mac(ip_address):
    mac_address = '52:54:' + ':'.join('%02x' % int(octet) for octet in ip_address.split('.'))
    return mac_address

def create(machine_type, values):
    """ Create a new virtual machine

        Required:
        * machine_type -> string, server or client
        * values       -> dict, values to use for substitution

        Returns:
        * None
    """
    template_dir = 'ingredients/libvirt'
    create_disk(values['name'])
    local(_apply_template(values, '%s/create_%s_%s.txt' % \
            (template_dir, machine_type, env['storage_type'])))

def create_disk(name):
    """ Create a new disk volume. Create the storage pool if it does not exist

        Requires:
        * name -> string, name of the volume to create

        Returns:
        None
    """
    if not has_pool(env['storage_pool']):
        create_pool(env['storage_pool'])
    if not has_volume(name):
        create_volume(name)

def convert_disk(name):
    """ Convert a volume to qcow2

        Requires:
        * name -> string, name of the disk to convert

        Return:
        * None
    """
    if env['storage_type'] == 'qcow2':
        local('qemu-img convert -O qcow2 "%s" "%s.qcow"' % (name, name))
        local('virsh edit "%s" path "%s.qcow"' % (name, name))

def has_snapshot(name, snapshot):
    return snapshot in list_snapshots(name).keys()

def list_snapshots(name):
    snapshots = {}
    with settings(hide('stdout', 'stderr', 'running')):
        output = local('virsh --connect %s snapshot-list %s | egrep -v "^ Name|^-|^$"' % (env['connect'], name), capture=True)
        for line in output.split('\n'):
            t = line.split()
            snapshots[int(t[0])] = " ".join([t[1], t[2], t[3]])
    return snapshots

def create_snapshot(name):
    """ Create a snapshot of a vm

        Requires:
        * name -> string, name of the VM to snapshot

        Returns:
        * None
    """
    local('virsh --connect %s snapshot-create "%s"' % (env['connect'], name))

def restore_snapshot(name, snapshot):
    """ Restore a snapshot of a vm

        Requires:
        * name -> string, name of the VM to restore

        Returns:
        * None
    """
    local('virsh --connect %s snapshot-revert "%s" %s' % (env['connect'], name, snapshot))

def remove_snapshot(name, snapshot):
    local('virsh --connect %s snapshot-delete "%s" %s' % (env['connect'], name, snapshot))

def disk_info(name):
    """ Print information about a volume

        Requires:
        * name -> string, name of the volume

        Returns:
        * None
    """
    if env['storage_type'] == 'qcow2':
        local('qemu-img info "%s"' % name)
    elif env['storage_type'] == 'lvm':
        local('lvdisplay %s' % name)

def has_network(name):
    return name in list_networks()

def list_networks():
    """ List the available networks

        Requires:
        * None

        Returns:
        * None
    """
    with settings(hide('stdout', 'stderr')):
        output = local('virsh --connect "%s" net-list --all | egrep -v "^Name|^-|^$" | awk "{print $1}"' % env['connect'], capture=True)
    return output.split('\n')

def start(name):
    """ Start a VM

        Requires:
        * name -> string, name of the VM

        Returns:
        * None
    """
    local('virsh --connect %s start "%s"' % (env['connect'], name))

def shutdown(name):
    """ Shutdown a VM
    
        Requires:
        * name -> string, name of the VM

        Returns:
        * None
    """
    local('virsh --connect %s shutdown %s' % (env['connect'], name))

def destroy(name):
    """ Destroy a VM

        Requires:
        * name -> string, name of the VM

        Returns:
        * None
    """
    local('virsh --connect %s destroy "%s"' % (env['connect'], name))

def remove(name):
    """ Completely remove a VM

        Requires:
        * name -> string, name of the VM

        Returns:
        * None
    """
    with settings(hide('warnings', 'stderr'), warn_only=True):
        destroy(name)
        local('virsh --connect %s undefine "%s"' % (env['connect'], name))
    vol_name = name.split('.')[0]
    print vol_name
    if has_volume(vol_name):
        remove_volume(vol_name)
    if has_volume(vol_name, ext='iso'):
        remove_volume(vol_name, ext='iso')

def has_node(name):
    return name in list_nodes()

def list_nodes():
    with settings(hide('stdout', 'stderr', 'running')):
        output = local('virsh --connect %s list --all | egrep -v "Id|^-|^$" | awk \'{print $2}\'' % (env['connect']), capture=True)
    return output.split('\n')

def has_pool(name):
    """ Check if a storage pool exists

        Requires:
        * name -> string, name of the pool

        Returns:
        * True, the pool exists
        * False, the pool does not exist
    """
    return name in list_pools()

def list_pools():
    """ List all available and online storage pools

        Required:
        * None

        Returns:
        * list, all available and online pools
    """
    result = local('virsh --connect %(connect)s pool-list | egrep -v \
                   \'^Name|^-|^$\' | awk \'{print $1}\'' % env, capture=True)
    return result.split('\n')

def refresh_pool(name):
    """ Refresh a storage pool

        Requires:
        * name -> string, name of the pool

        Returns:
        * None
    """
    local('virsh --connect %s pool-refresh %s' % (env['connect'], name))

def create_pool(name):
    """ Creates a new directory or LVM based storage pool

        Requires:
        * name -> string, name of the new pool

        Returns:
        * None
    """
    if env['storage_pool'] == 'default':
        return
    else:
        values = env.copy()
        with settings(hide('stdout')):
            values['storage_owner_uid'] = run('id -u %s' % env['storage_owner'])
            values['storage_owner_gid'] = run('id -g %s' % env['storage_owner'])
        values['name'] = name
    if env['storage_type'] == 'qcow2':
        _apply_template(values, \
                        'ingredients/libvirt/pool-qcow2.xml', \
                        '/tmp/%s.xml' % name)
        local('virsh --connect %s pool-define /tmp/%s.xml' % (env['connect'], \
                                                              name))
        local('virsh --connect %s pool-build %s' % (env['connect'], name))
    elif values['storage_type'] == 'lvm':
        run('sudo /sbin/vgcreate %s /dev/%s/%s' % (name, env['volumegroup'], \
                                                   name))
        local('virsh --connect %s pool-define-as %s logical --target \
              /dev/%s/%s' % (env['connect'], name, env['volumegroup'], name))
    local('rm -f /tmp/%s.xml' % name)
    local('virsh --connect %s pool-autostart %s' % (env['connect'], name))
    local('virsh --connect %s pool-start %s' % (env['connect'], name))

def remove_pool(name):
    """ Remove a storage pool

        Requires:
        * name -> string, name of the storage pool

        Returns:
        * None
    """
    if env['storage_pool'] == 'default':
        return
    for volume in list_volumes(name):
        remove_volume(volume.replace('.img', ''))
    with settings(hide('warnings', 'stderr'), warn_only=True):
        local('virsh --connect %s pool-destroy %s' % (env['connect'], name))
        local('virsh --connect %s pool-delete %s' % (env['connect'], name))
        local('virsh --connect %s pool-undefine %s' % (env['connect'], name))

def has_volume(name, ext='img'):
    """ Check if a volume exists within the default configured storage pool

        Requires:
        * name -> string, name of the volume
    
        Optional:
        * ext -> string, 'img' or 'iso'. Defaults to 'img'

        Returns:
        * True, the volume exists
        * False, the volume does not exist
    """
    if env['storage_type'] == 'qcow2':
        return '%s.%s' % (name, ext) in list_volumes(env['storage_pool'])
    elif env['storage_type'] == 'lvm':
        return name in list_volumes(env['storage_pool'])

def list_volumes(name):
    """ List all available volumes within a storage pool

        Requires:
        * name -> string, name of the pool

        Returns:
        * list, all available volumes within the pool
    """
    result = local('virsh --connect %s vol-list %s | egrep -v \'^Name|^-|^$\' \
                   | awk \'{print $1}\'' % (env['connect'], name), capture=True)
    return result.split('\n')

def create_volume(name, ext='img'):
    """ Create a new volume within the default configured storage pool

        Required:
        * name -> string, name of the volume

        Optional:
        * ext -> string, 'img' or 'iso'. Defaults to 'img'

        Returns:
        * None
    """
    values = env.copy()
    values['name'] = name
    values['disk_size'] = int(env['disk_size']) * 1024 * 1024 * 1024
    with settings(hide('stdout')):
        values['storage_owner_uid'] = run('id -u %s' % env['storage_owner'])
        values['storage_owner_gid'] = run('id -g %s' % env['storage_owner'])
    if values['storage_pool'] == 'default':
        values['storage_path'] = '%s/%s.%s' % (env['storage_dir'], name, ext)
    else:
        values['storage_path'] = '%s/%s/%s.%s' % (env['storage_dir'], \
                                                  env['storage_pool'], \
                                                  name, ext)
    if env['storage_type'] == 'qcow2':
        if ext == 'img':
            _apply_template(values, \
                            'ingredients/libvirt/vol-qcow2.xml', \
                            '/tmp/%s.xml' % name)
        else:
            _apply_template(values, \
                            'ingredients/libvirt/vol-iso.xml', \
                            '/tmp/%s.xml' % name)
        local('virsh --connect %s vol-create %s /tmp/%s.xml' % \
                (env['connect'], env['storage_pool'], name))
    elif values['storage_type'] == 'lvm':
        # BROKEN, see https://bugzilla.redhat.com/show_bug.cgi?id=714986
        #local('virsh --connect %(connect)s vol-create-as %(storage_pool)s \
        #       %(name)s %(disk_size)sG ' % values)
        if env['host'] == 'localhost':
            local('sudo /sbin/lvcreate --name %s -L %sG %s' % \
                    (name, env['disk_size'], env['volumegroup']))
        else:
            run('sudo /sbin/lvcreate --name %s -L %sG %s' % \
                    (name, env['disk_size'], env['volumegroup']))
    local('rm -f /tmp/%s.xml' % name)

def remove_volume(name, ext='img'):
    """ Remove a volume from the default configured storage pool

        Requires:
        * name -> string, name of the volume

        Optional:
        * ext -> string, 'img' or 'iso'. Defaults to 'img'

        Returns:
        * None
    """
    if not name:
        return
    values = env.copy()
    values['name'] = name
    values['ext'] = ext
    local('virsh --connect %s vol-delete %s.%s --pool %s' % \
            (env['connect'], name, ext, env['storage_pool']))

def seed_prepare(fqdn):
    print('[libvirt.seed_prepare]: Function not implemented')

def uname():
    local('uname -a')
