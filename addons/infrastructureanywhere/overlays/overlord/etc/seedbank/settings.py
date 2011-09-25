"""seedbank Configuration (c) 2009-2011 - Jasper Poppe <jpoppe@ebay.com>"""

"""daemon/server settings"""
server = {
    'listen': '',
    'address': '192.168.20.1',
    'port': '7467'
}

"""valid distros and list of distros which do not have "non free" firmwares included, feel free to add ;)"""
setup_dists = {
    'releases': ('debian-lenny-amd64', 'debian-lenny-i386',
                 'debian-squeeze-amd64', 'debian-squeeze-i386',
                 'debian-sid-amd64', 'debian-sid-i386',
                 'ubuntu-lucid-i386', 'ubuntu-lucid-amd64',
                 'ubuntu-maverick-i386', 'ubuntu-maverick-amd64',
                 'ubuntu-natty-i386', 'ubuntu-natty-amd64'),
    'firmwares': ('debian-lenny-amd64', 'debian-lenny-i386',
                  'debian-squeeze-amd64', 'debian-squeeze-i386')
}

"""urls for getting pxe boot files, syslinux"""
setup_urls = {
    #'debian': 'http://ftp.debian.org',
    'debian': 'http://192.168.122.1/seedbank',
    'ubuntu': 'http://archive.ubuntu.com',
    'syslinux': 'http://192.168.122.1/seedbank/syslinux-4.04.tar.gz',
    #'syslinux': 'http://www.kernel.org/pub/linux/utils/boot/syslinux/4.xx/syslinux-4.04.tar.gz',
    #'firmware': 'http://cdimage.debian.org/cdimage/unofficial/non-free/firmware/${release}/current/firmware.tar.gz'
    'firmware': 'http://192.168.122.1/seedbank/${release}/firmware.tar.gz'
}

"""seedbank paths"""
sp_paths = {
    'archives': '/var/cache/seedbank/archives',
    'seeds': '/etc/seedbank/seeds',
    'tftpboot': '/var/lib/tftpboot',
    'recipes': '/etc/seedbank/recipes',
    'templates': '/etc/seedbank/templates',
    'manifests': '/etc/seedbank/manifests',
    'overlays': '/etc/seedbank/overlays',
    'files': '/etc/seedbank/www',
    'udebs': '/etc/seedbank/udebs'
}

"""general settings"""
settings = {
    'log_file': '/var/log/seedbank.log',
    'disable_hooks': False
}

late_commands = [
    'wget -q -O - http://%s:%s/disable?address=${address}' % (server['address'], server['port']),
    'wget http://192.168.122.1/debian/jpoppe.key -O /target/root/jpoppe.key',
    'echo -e \"blacklist ipv6\\nalias net-pf-10 off\\nalias ipv6 off\\n\" > /target/etc/modprobe.d/disable_ipv6.conf',
    'in-target apt-key add /root/jpoppe.key',
    'in-target apt-get update',
    'in-target sed -i s/allow-hotplug/auto/ /etc/network/interfaces',
    'echo "192.168.20.1 puppet" >> /target/etc/hosts'
]

bootstrap_commands = [
    'wget http://%s:%s/bootstrapinit?address=${address} -O /target/etc/init.d/seedbank-bootstrap' % (server['address'], server['port']),
    'chmod 755 /target/etc/init.d/seedbank-bootstrap',
    'in-target update-rc.d seedbank-bootstrap defaults'
]

"""
seedfile variables, feel free to add or change, variable format 
in the seed files / recipes = *variable

if there is 'command' in the key like "earlycommand" you can also 
use the address variable here format: ${address} and those will
be replaced before variables in the seed file will be replaced
"""
settings_seedfile = {
    'user': 'seedbank',
    'userfullname': 'seedbank User',
    'username': 'seedbank',
    'userpassword': 'seed123',
    #'addkernelopts': 'console=ttyS0,115200n8',
    'addkernelopts': '',
    'debian_packages': 'openssh-server puppet debconf-utils lsb-release vim less',
    'debian_mirrorhostname': '192.168.122.1',
    'debian_mirrordirectory': '/debian/mirror',
    #'debian_mirrorhostname': 'packages.ritalin.emc.local',
    #'debian_mirrordirectory': '/debian/mirror',
    #'debian_mirrorhostname': 'mirrors.nl.kernel.org',
    #'debian_mirrordirectory': '/debian',
    'ubuntu_packages': 'openssh-server puppet debconf-utils lsb-release vim less',
    #'ubuntu_packages': 'openssh-server puppet debconf-utils lsb-release vim less firefox compiz pulseaudio terminator',
    #'ubuntu_mirrorhostname': 'packages.ritalin.emc.local',
    #'ubuntu_mirrordirectory': '/ubuntu/mirror',
    'ubuntu_mirrorhostname': 'nl.archive.ubuntu.com',
    'ubuntu_mirrordirectory': '/ubuntu',
    'timezone': 'Europe/Amsterdam',
    'ntpserver': 'ntp.xs4all.nl',
    'earlycommand': 'wget -q -O - http://%s:%s/pimp?address=${address}' % (server['address'], server['port']),
    'latecommand': ';'.join(late_commands),
    'bootstrapcommand': ';'.join(bootstrap_commands),
    'overlayscommand': 'cd /target && wget http://%s:%s/overlay.tgz?address=${address} -O - | tar zxvf -' % (server['address'], server['port'])
}

"""manifests variables, feel free to add more or change, variable format = ${variable}"""
settings_manifests = {
    'template': 'seedbank-bootstrap',
    'command': '/usr/bin/puppet --clientbucketdir /var/lib/puppet/clientbucket --debug /seedbank/$manifest >> /tmp/seedbank-bootstrap.log'
}

"""pxe variables, feel free to add more or change, variable format = ${variable}"""
settings_pxe = {
    'template': 'pxehost',
    'locale': 'en_US',
    'countrychooser': 'NL',
    'console_layout': 'us',
    'console_charmap': 'UTF-8',
    'interface': 'eth0',
    'debug_level': '0',
    'extra': 'netcfg/dhcp_timeout=60 debian-installer/allow_unauthenticated=true',
    #'extra': 'console=ttyS0,115200n8 netcfg/dhcp_timeout=60 debian-installer/allow_unauthenticated=true',
    'theme': 'dark'
}

"""command(s) to run after enabling host(s) with seedbank"""
hooks_enable = {
    #'seedprep': 'seedprep.py -a ${hostname}.${domainname}'
    'puppet': 'puppet cert --clean ${hostname}.${domainname}'
}

"""command(s) to run after host has been installed"""
hooks_disable = {
    #'seedprep': 'seedprep.py -r ${hostname}.${domainname}'
}

"""external nodes use False to disable, use prefix http(s):// for url, use string for script"""
external_nodes = {
    'provider': False
    #'provider': 'seednode.py -H ${hostname}.${domainname}',
    #'address': 'external_mac_1'
}
