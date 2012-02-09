from __future__ import with_statement
from fabric.api import env, local, run, put, settings

env.hosts = ['overlord001.a.c.m.e']
#env.hosts = ['overlord001.h.o.m.e']
env.user = 'root'
application = 'seedbank'
version = '1.1.0'
deb_file = 'seedbank_%s_all.deb' % version
repository = '/home/www/repositories/debian/sn'

def bump_version():
    local('find . -type f -name "*seed*.py" | while read file; do sed -i "s/__version__ .*/__version__ = \'%s\'/" ${file}; done' % version)
    local('sed -i "s/    version=.*/    version=\'%s\',/" setup.py' % version)
    local('sed -i "s/    version=.*/    version=\'%s\',/" setup.py' % version)
    local('sed -i "s/version = .*/version = \'%s\'/" manual/conf.py' % version)
    local('sed -i "s/release = .*/release = \'%s\'/" manual/conf.py' % version)

def build():
    local('dpkg-buildpackage -b -tc')
    local('mv ../%s*.deb ../%s_*.changes ~/builds' % (application, application))

def repo_add():
    local('reprepro -Vb %s includedeb squeeze ~/builds/%s' % (repository, deb_file))
    
def repo_remove():
    with settings(warn_only=True):
        local('reprepro -Vb %s remove squeeze %s' % (repository, application))

def localhost():
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
