from __future__ import with_statement
from fabric.api import env, local, run, put, settings

import os
import sys

env.hosts = ['overlord001.a.c.m.e']
#env.hosts = ['overlord001.h.o.m.e']
env.user = 'root'
application = 'seedbank'
version = '2.0.0rc4'
deb_file = 'seedbank_%s_all.deb' % version
repository = '/home/www/repositories/debian/sn'
puppet = '~/git/ecg-puppet-staging/modules/xx/platform/xx_overlord/templates/etc/seedbank'

fab_path = os.path.dirname(os.path.realpath(__file__))
if not os.path.dirname(os.path.realpath(__file__)) == os.getcwd():
    print ('please run fabric from "%s"' % fab_path)
    sys.exit(1)

def bump_version():
    local('find ./seedbank -type f -name "*.py" | grep -v bottle.py | while read file; do sed -i "s/__version__ .*/__version__ = \'%s\'/" ${file}; done' % version)
    local('sed -i "s/    version=.*/    version=\'%s\',/" setup.py' % version)
    local('sed -i "s/    version=.*/    version=\'%s\',/" setup.py' % version)
    local('sed -i "s/version = .*/version = \'%s\'/" manual/conf.py' % version)
    local('sed -i "s/release = .*/release = \'%s\'/" manual/conf.py' % version)
    local('dch')

def build():
    local('dpkg-buildpackage -b -tc')
    local('mv ../%s*.deb ../%s_*.changes ~/builds' % (application, application))

def repo_add():
    local('reprepro -Vb %s includedeb squeeze ~/builds/%s' % (repository, deb_file))
    
def repo_remove():
    with settings(warn_only=True):
        local('reprepro -Vb %s remove squeeze %s' % (repository, application))

def localhost():
    local('sudo rm -rf /etc/seedbank')
    local('sudo ./setup.py install; sudo rm -rf build/')
    local('sudo ln -s ~/git/ecg-puppet-staging /etc/seedbank/overlays/iso_overlord/root/')
    local('sudo ln -s ~/git/ecg-puppet-staging /etc/seedbank/overlays/iso_overlord_vbox/root/')
    build()
    repo_remove()
    repo_add()

def test():
    localhost()
    run('apt-get update')
    run('apt-get --force-yes --yes purge %s' % application)
    run('rm -rf /etc/%s' % application)
    run('apt-get --assume-yes install %s' % application)
    run('/etc/init.d/%s start' % application)

def test_remote():
    build()
    put('~/builds/%s' % deb_file, '/root')
    run('apt-get --force-yes --assume-yes purge %s' % application)
    run('rm -rf /etc/%s' % application)
    run('dpkg -i %s' % deb_file)

def test_seedslave():
    build()
    run('cp /etc/seedbank/settings.py /root')
    put('~/builds/%s' % deb_file, '/root')
    run('apt-get --force-yes --assume-yes purge %s' % application)
    run('rm -rf /etc/%s' % application)
    run('dpkg -i %s' % deb_file)
    run('cp /root/settings.py /etc/seedbank')
    run('/etc/init.d/%s start' % application)

def update_puppet():
    puppet_conf = os.path.join(puppet, 'conf.d')
    local('cp ~/git/seedbank/etc/seedbank/settings.yaml %s' % puppet)
    local('cp ~/git/seedbank/etc/seedbank/conf.d/* %s' % puppet_conf)
