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
from fabric.api import local, run, put, settings, cd, lcd, hide
from fabric.contrib.files import exists

import os
import string
import sys
import urllib

def _apply_template(values, file_name):
    contents = string.Template(open(file_name, 'r').read())
    contents = contents.substitute(values)
    open(file_name, 'w').write(contents)

def _available_iso():
    available = []
    with cd(env['storage_dir']):
        with settings(hide('stdout', 'stderr'), warn_only=True):
            for line in run('ls debian-*-*-netinst.iso 2>/dev/null').split('\n'):
                available.append(line)
    available.sort()
    if len(available) > 0:
        return os.path.basename(available[len(available)-1])

def clean(name):
    local('rm -rf %(work_dir)s' % env)
    run('rm -rf %(work_dir)s' % env)
    run('rm -f "%s/%s.iso"' % (env['storage_dir'], name))

def prepare():
    local('mkdir -p %(work_dir_local)s' % env)
    run('mkdir -p %(work_dir_remote)s' % env)
    run('test -d %(git_target)s || mkdir -p %(git_target)s' % env)
    #run('test -d /opt/acmefactory || mkdir /opt/acmefactory')

def get_iso():
    cur_iso = _available_iso()
    if not cur_iso:
        for line in urllib.urlopen(env['iso_url']).readlines():
            if 'netinst' in line:
                cur_iso = line.split('"')[5]
        target = os.path.join(env['storage_dir'], cur_iso)
        if not cur_iso:
            print('Failed to locate latest iso')
            sys.exit(1)
        if not os.path.exists(target):
            run('wget --progress=dot:mega -c -O %s.new %s/%s' % (target, env['iso_url'], cur_iso))
            run('mv %s.new %s' % (target, target))

def extract_iso():
    values = env
    values['iso'] = _available_iso()
    run('mkdir -p %(work_dir_remote)s/iso' % values)
    run('bsdtar -C %(work_dir_remote)s/iso -xf %(storage_dir)s/%(iso)s' % values)
    run('chmod -R u+w %(work_dir_remote)s/iso' % values)

def auto_boot_iso():
    # put('%(git_dir)s/acmefactory/ingredients/isolinux.cfg' % env, '%(work_dir_remote)s/iso/isolinux/isolinux.cfg' % env)
    put('ingredients/isolinux.cfg' % env, '%(work_dir_remote)s/iso/isolinux/isolinux.cfg' % env)

def add_seedfile(values):
    # local('cp %(git_dir)s/acmefactory/ingredients/overlord.seed %(work_dir_local)s/preseed.cfg' % env)
    local('cp ingredients/overlord.seed %(work_dir_local)s/preseed.cfg' % env)
    _apply_template(values, '%(work_dir_local)s/preseed.cfg' % env)
    run('mkdir %(work_dir_remote)s/initrd' % env)
    put('%(work_dir_local)s/preseed.cfg' % env, '%(work_dir_remote)s/initrd' % env)
    with settings(warn_only=True):
        with cd('%(work_dir_remote)s/initrd' % env):
            run('gzip -d < ../iso/install.amd/initrd.gz | cpio --extract --make-directories --no-absolute-filenames' % env)
    with cd('%(work_dir_remote)s/initrd' % env):
        run('find . | cpio -H newc --create | gzip -1 > ../iso/install.amd/initrd.gz')

def prepare_overlay(values):
    # local('cp -r %(git_dir)s/acmefactory/overlays/%(overlay)s %(work_dir_local)s/overlay' % values)
    local('cp -r overlays/%(overlay)s %(work_dir_local)s/overlay' % values)
    local('mkdir -p %(work_dir_local)s/overlay/root/.ssh' % values)
    local('cp %(home_dir)s/.ssh/id_rsa.pub %(work_dir_local)s/overlay/root/.ssh/authorized_keys' % values)
    _apply_template(values, '%(work_dir_local)s/overlay/etc/network/interfaces' % values)
    _apply_template(values, '%(work_dir_local)s/overlay/etc/hosts' % values)

def auto_puppet():
    # local('cp %(git_dir)s/acmefactory/ingredients/puppet_bootstrap %(work_dir_local)s/overlay/etc/runonce.d/puppet_bootstrap.enabled' % env)
    local('cp ingredients/puppet_bootstrap %(work_dir_local)s/overlay/etc/runonce.d/puppet_bootstrap.enabled' % env)

def push_overlay():
    put('%(work_dir_local)s/overlay' % env, '%(work_dir_remote)s' % env)
    run ('chmod 755 %(work_dir_remote)s/overlay/etc/rc.local' % env)

def add_puppet_repo():
    values = env
    values['extdata_file'] = '%s.csv' % ('-'.join(env['dns_domain'].split('.')[:2]))
    if exists(os.path.join(values['git_target'], values['git_repo'])):
        sync_git()
    else:
        push_git()
    local('cp %(git_dir)s/%(git_repo)s/modules/xx/platform/xx_base_system/extdata/%(extdata_file)s %(work_dir_local)s' % values)
    #
    #
    #_apply_template(values, '%(work_dir_local)s/%(extdata_file)s' % values)
    #
    put('%(work_dir_local)s/%(extdata_file)s' % values, '%s' % os.path.join(values['git_target'], values['git_repo'], 'modules/xx/platform/xx_base_system/extdata'))
    with cd(env['git_target']):
        run('tar cf - %(git_repo)s | (cd %(work_dir_remote)s/overlay/root; tar xfp -)' % env)

def push_git():
    with lcd('%(git_dir)s' % env):
        local('tar --exclude="\.git" -jcf %(work_dir_local)s/puppet_repo.tar.bz2 %(git_repo)s' % env)
    put('%(work_dir_local)s/puppet_repo.tar.bz2' % env, '%(work_dir_remote)s/%(git_repo)s.tar.bz2' % env)
    with cd(env['git_target']):
        run('tar jxf %(work_dir_remote)s/%(git_repo)s.tar.bz2' % env)

def sync_git():
    git_path = os.path.join(env['git_dir'], env['git_repo'])
    if env['hosts'][0] == 'localhost':
        local('rsync -avr --exclude="/%s/.git" %s %s/' % (env['git_repo'], git_path, env['git_target']))
    else:
        local('rsync -e ssh -avr --exclude="/%s/.git" %s %s@%s:%s/' % (env['git_repo'], git_path, env['user'], env['hosts'][0], env['git_target']))

def tar_overlay():
    with cd('%(work_dir_remote)s/overlay' % env):
        run('tar --owner=root -cf %(work_dir_remote)s/iso/overlay.tar *' % env)

def gen_md5sums():
    with cd(os.path.join(env['work_dir_remote'], 'iso')):
        run('md5sum $(find ! -name "md5sum.txt" ! -path "./isolinux/*" -follow -type f) > md5sum.txt')

def create_iso(name):
    with cd(env['work_dir_remote']):
        if env['storage_pool'] == 'default':
            iso = '%s/%s.iso' % (env['storage_dir'], name)
        else:
            iso = '%s/%s/%s.iso' % (env['storage_dir'], env['storage_pool'], name)
        run('genisoimage -quiet -o "%s" -r -J -no-emul-boot -boot-load-size 4 -boot-info-table -b isolinux/isolinux.bin -c isolinux/boot.cat iso' % iso)
        run('chmod 664 %s' % iso)

def breed(name, ip_address, puppet, overlay):
    values = env
    values['ip_address'] = ip_address
    values['host_name'] = name
    values['overlay'] = overlay

    clean(name)
    prepare()
    get_iso()
    extract_iso()
    auto_boot_iso()
    add_seedfile(values)
    prepare_overlay(values)
    if puppet:
        auto_puppet()
    push_overlay()
    if puppet:
        add_puppet_repo()
    tar_overlay()
    gen_md5sums()
    create_iso(name)

if __name__ == 'chicken':

    from fabric.api import env

    if not env['hosts']:
        env['hosts'] = ['localhost']
    elif len(env['hosts']) > 1:
        print ('error: this script works only with 1 host at the same time')
        sys.exit()

    defaults = {
        'storage_dir': '/var/lib/libvirt/images',
        'git_dir': os.path.expanduser('~/git'),
        'git_repo': 'ecg-puppet-staging',
        'git_target': '/tmp/chicken/acmefactory',
        'home_dir': os.path.expanduser('~'),      # Home directory
        'iso': 'debian-6.0.1a-amd64-netinst.iso',
        'iso_url': 'http://cdimage.debian.org/debian-cd/6.0.1a/amd64/iso-cd',
        'repository': '192.168.122.1',
        'work_dir': '/tmp/chicken',   # What to use as a working directory
        'work_dir_local': '/tmp/chicken/local',   # What to use as a working directory
        'work_dir_remote': '/tmp/chicken/remote' # What to use as a working directory
    }

    for key in defaults.keys():
        if not key in env.keys():
            env[key] = defaults[key]
