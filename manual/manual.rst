===============
seedBank Manual
===============

.. contents:: seedBank Manual
    :local:

----------------
Quickstart Guide
----------------

Install seedBank
================

Follow the instructions on http://www.infrastructureanywhere.com/seedbank/downloads.html.

seedBank ISO
============

Introduction
------------

This section will describe how to create a fully unattended Debian or Ubuntu
installation ISO.

Build an unattended installation ISO
------------------------------------

Run the **seedbank list --isos** command to list the names of the available ISOs::

    seedbank list --help
    seedbank list -i

Choose the name of the ISO you want to use as a base for creating the
unattended installation ISO. Run 'seedbank manage --iso <iso_name>' to download
the install ISO. This ISO will be cached for future use so you only have to be
download it once. In this example the Debian Jessie AMD64 mini ISO will be used. The advantage of the mini ISOs is that it is really small to download, the disadvantage is that all the packages which are needed for the installation will be downloaded from a mirror::

    seedbank manage --help
    seedbank manage -i debian-jessie-amd64-mini

Build the ISO with the **seedbank iso --aditional-seeds <additional_seed> <host_name> <iso_name> <ouput>** command, by default the ISO will be saved a <fqdn>.iso, in case of this example this will be *squeeze001.domain.iso*. If you do not specify the additional-seed the installer will require manual input for disk partitioning, be sure to match the disk recipe with the configuration of the node to be installed::

    seedbank iso --help
    seedbank list --seeds

For SCSI/SATA disks::

    seedbank iso -a 1disk_sd_one_partition -r debian-jessie-amd64-mini jessie001.domain

For IDE disks::

    seedbank iso -a 1disk_hd_one_partition -r debian-jessie-amd64-mini jessie001.domain

For Virtual disks (Used by some virtualization disk controller drivers)::

    seedbank iso -a 1disk_vd_one_partition -r debian-jessie-amd64-mini jessie001.domain

seedBank PXE
============

Introduction
------------

Unattended pxe/network installations are pretty complicated because it relies on many components of an infrastructure. This section will help you to configure a seedBank server so you are able to do fully unattended Debian or Ubuntu netboot installs.

seedBank aims to simplify this process as much as possible. If you do not have the knowledge yet but still want to do those cool runatttended pxe/network installations start reading on the net about those subjects. With some patience and practice it is definately possible, in the end it is no rocket science ;)

Knowledge about DHCP, DNS and TFTP is required for being able to do network installs.

This section assumes you have the following infrastructure, adopt it to your own needs:

seedBank server which will also run the DHCP, TFTP and DNS services (This should be a Linux server with Python 2.6 or 2.7)::

    Hostname: seedbank001.intern.local
    IP Address: 192.168.0.1

seedBank client which we are going to install::

    Hostname: seednode001.intern.local
    IP Address: 192.168.0.20

Prerequisites
-------------

To be able to do PXE/network you will need to have the following components available in your infrastructure:

* A connection to the internet (for downloading resources like netboot images, ISOs, etc.)
* TFTP Server
* DHCP Server
* An additional host/virtual host for installing which is able to boot via PXE

Optional but recommended:

* DNS Server (You could also use */etc/hosts* (on the seedBank server) or use MAC address based installations)
* Custom Debian/Ubuntu mirror(s), see the `Create a Debian or Ubuntu mirror`_ chapter for more information.

Different flavours of DNS, TFTP or DHCP servers can be used. For an easy and lightweight all in one solution you could use dnsmasq, see the `Configure dnsmasq`_ chapter for information about setting up dnsmasq for TFTP, DHCP and DNS.

It is recommended to gather some knowledge about the Debian preseed system, the predefined preseed files in */etc/seedbank/seeds* should be sufficient for most people. But there are much more settings available.

Configure default settings
--------------------------

seedBank configuration files are in the the YAML format (except for the logging). It is a wise idea to create a backup of the configuration before you start editing the configuration. It is recommended scan quickly through the configuration files in the */etc/seedbank* directory so you will get an idea about the possibilities.

Create a backup of the current seedBank configuration::

    sudo cp -r /etc/seedbank{,-org}

Edit the **settings.yaml** file, replace the IP address of the *seed_host* variable with the IP address or fully qualified domain name of the seedBank server::

    sudo vi /etc/seedbank/settings.yaml

After editing the settings.yaml file the seedBank daemon needs to be restarted so it will read the new settings::

    sudo /etc/init.d/seedbank restart

You probably also want to customize the 'variables.yaml' configuration file. The settings are described in the file::

    sudo vi /etc/seedbank/conf.d/variables.yaml

Get the netboot image and syslinux files
----------------------------------------

The **seedbank manage** command is used for downloading and preparing the Debian Squeeze netboot image.

List the available netboot distributions with the **seedbank list --netboots** command::

    seedbank list --help
    seedbank list -n

Download and install the required syslinux files to */var/lib/tftpboot* (Only needs to be done once)::

    seedbank manage --help
    sudo seedbank manage -s

Download the Debian Jessie netboot image tar archive and extract it to the right place (Only need to be done once)::

    sudo seedbank manage -n debian-jessie-amd64

Generate the pxelinux configuration file
----------------------------------------

Run the following command on the seedBank server after reading the explanation below::

    seedbank pxe --help

For SCSI/SATA disks::

    sudo seedbank pxe -a 1disk_sd_one_partition -r debian-jessie-amd64 seednode001.intern.local

For IDE disks::

    sudo seedbank pxe -a 1disk_hd_one_partition -r debian-jessie-amd64 seednode001.intern.local debian-jessie-amd64

For Virtual disks (Used by some virtualization disk controller drivers)::

    sudo seedbank pxe -a 1disk_vd_one_partition -r debian-jessie-amd64 seednode001.intern.local

Explanation:

This command will generate the pxelinux configuration for the host we want to install (seednode001.intern.local).

The -a option specifies an additional seed file which will be appended at the end of the chosen preseed file, disk recipes are also preseed files so this option will use the disk recipe which is located at */etc/seedbank/seeds/1disk_xd_one_partition.seed*.

The seed file which will be used is chosen automatically, it takes the second part of the chosen distribution, so in this case the second part of *debian-jessie-amd64* is jessie. seedBank will now use */etc/seedbank/seeds/jessie.seed* as the main preseed file. This behaviour can be overridden with the -s (--seed) option. So if you want to use another main preseed file, for example seednode001.seed instead of jessie.seed run the following command::

    sudo seedbank pxe -a 1disk_sd_one_partition -s seednode001 -r debian-jessie-amd64 seednode001.intern.local

The seedBank command will generate */var/lib/tftpboot/pxelinux.cfg/C0A80014*. The filename is actually the IP address converted to hexidecimal, 192.168.0.20 in hexidecimal is C0A80014. This file contains information which is used by the node as soon it boots via PXE. 

Show the contents of the generated PXE file::

    cat /var/lib/tftpboot/pxelinux.cfg/C0A80014

Configure DHCP
--------------

Configure the DHCP server so the 'seednode001.intern.local' node will get the correct IP address asigned (in this example: 192.168.0.20).

Boot the seedBank node
======================

Cross your fingers and boot the 'seednode001.intern.local' node. If everything went right you should see the Debian installer doing his job fully automated, congratiulations! If not there could be many reasons, don't give up yet! See for example the troubleshooting section for more information.

Advanced Example 1
==================

In this example it is described how to install an Ubuntu Precise Pangolin node, copy a custom file overlay over the file system at the end of the installation, and use custom variables in the templates and run a standalone Puppet manifest at the end of the first boot of the node. We will call the node 'ubuntu001.intern.local'.

Download the Ubuntu Precise Pangolin netboot image archive and extract it to the right place (Only needs to be done once)::

    sudo seedbank manage -n ubuntu-precise-amd64

The following steps will be done when preparing a netboot image

- Check if the netboot image archive is already cached on the system (*/var/cache/seedbank/archives/ubuntu-precise-amd64/netboot.tar.gz*)
- If not it will download the netboot image archive to '/var/cache/seedbank/archives/ubuntu-precise-amd64/netboot.tar.gz'
- Extract the netboot image archive to */tmp/seedbank/manage*
- Copy 'linux' and the 'initrd.gz' image to */var/lib/tftpboot/seedbank/ubuntu-precise-amd64*
- Remove the temporary files

Create a custom file overlay with a custom script which will be run once at the end of the first boot after the installation::

    sudo mkdir -p /etc/seedbank/overlays/custom_overlay/etc/runonce.d
    echo "touch /seedbank_custom_overlay_test" > /etc/seedbank/overlays/custom_overlay/etc/runonce.d/custom_overlay_test.enabled
    echo "${fqdn}" > /etc/seedbank/overlays/custom_overlay/another_custom_overlay_test.sb_template
    echo 'this is a static file' > /etc/seedbank/overlays/custom_overlay/the_static_file_custom_overlay_test

To customize file permissions for a custom file overlay you can generate a permissions file which will be applied at the end of an installation::

    sudo seedbank manage -o custom_overlay

Now you can customize the generated permissions file, see the permissions file for an explanation about how to customize it::

    sudo vi /etc/seedbank/overlays/custom_overlay.permissions

Since we have downloaded the required files and have the custom file overlay in place we generate the pxelinux configuration file for the  node we want to install::

    sudo seedbank pxe -m  -o custom_overlay -a 1disk_sd_one_partition -p example -v custom custom_variable -r ubuntu-precise-amd64 ubuntu001.intern.local

Explanation of the command:

- sudo -> become root so you will have permissions to write files in the tftpboot directory
- -m -> MAC address of the NIC from the node to install, since a MAC address has been specified there is no need of a DNS entry for ubuntu001.intern.local
- pxe -> the seedBank command to run
- -o custom_overlay -> specify the custom overlay directory you want to copy over the file system
- -a 1disk_sd_one_partition -> specify an additional seed file to append to the main seed file, in this case we spefify a disk recipe, so the install will be done fully unattended, this will also WIPE ALL DATA DURING THE INSTALLATION ON THE TARGET MACHINE (Since we did not specify the main seed file with the -s (--seed) option seedbank will automatically use the preseed with the name of the distribution we want to install, in this case it will use precise.seed)
- -p example -> run the example Puppet Manifest (/etc/seedbank/manifests/example.pp) during the first boot after the installation.
- -v specify additional variables which will be stored in the generated pxelinux configuration file
- -r ubuntu-precise-amd64 -> the release to install, the default release to use could be configured in '/etc/seedbank/conf.d/system.yaml' in the 'default_release' section
- ubuntu001.intern.local -> the fully qualified domain name of the node to install

Advanced Example 2
==================

All seed and PXE variables can be overridden can be overriden with a config override file. Command line arguments can also be overridden with a config override file. For an example see /etc/seedbank/configs/iso_foo.foobar.com.yaml.

To create an ISO named '/tmp/foo.foobar.com.iso' run the following command::

    sudo seedbank iso -c iso_foo.foobar.com

Config overrides could also be used for PXE netboot installations.

seedBank Commands
=================

This section describes how to use the seedBank options, if this is the first time you will use seedBank please first read/modify /etc/seedbank/settings.yaml, /etc/seedbank/variables.yaml and read the quick start guide.

Main Application
================

.. include:: manual/help/seedbank

List Command
============

List resources like netboot images, seed files, Puppet manifests, configuration overrides, file overlays, pxelinux.cfg files, netboot images and ISOs

Help Output
-----------

.. include:: manual/help/seedbank_list

PXE Command
===========

.. include:: manual/help/seedbank_pxe

ISO Command
===========

.. include:: manual/help/seedbank_iso

Manage Command
==============

.. include:: manual/help/seedbank_manage

--------
Examples
--------

Download the syslinux archive and put the files required for a netboot installation in the right place. Download the Debian Jessie AMD64 netboot image and put it in the right place::

    seedbank manage
    seedbank manage --syslinux

Prepare an installation for Debian Jessie amd64 with the minimal required options (DNS should be configured properly since it will gather the IP address via a DNS lookup)::

    seedbank pxe minion001.a.c.m.e

NOTE: Since no release has been specified in this example seedBank will look for the default release which is normally configured in the '/etc/seedbank/conf.d/system.yaml' file in the 'default_release' section. By default this value is for pxe installations 'debian-jessie-amd64'.

NOTE: if the default configuration (seed files) are used the installation will require user input for partitioning the disks, to do a fully unattended installation a disk recipe should be added to the command::

    seedbank pxe -a 1disk_sd_one_partition minion001.a.c.m.e

Prepare an installation for Ubuntu Precise with a custom disk layout, run the Puppet network manifest after the installation and specify some custom PXE variable which could be used in the file overlay templates::

    seedbank pxe -a 1disk_sd_one_partition -p network -o minion -r ubuntu-natty-amd64 minion001.a.c.m.e

---------------
Troubleshooting
---------------

Introduction
============

This section is to help you out with troubleshooting seedBank problems, seedBank depends on external resources to function properly.

Logging
=======

seedBank logs quite some information by default.

The default log file is /var/log/seedbank.log and the default log level is INFO, change this to the DEBUG level to get debug information::

    vi /etc/seedbank/logging.conf

If somethings goes wrong during the installation the Debian installer provides several options for debugging. You can switch to the different consoles by using the ALT and arrow keys, or by using the ALT key and the number of the specific console.

* ALT+1 The default console
* ALT+2 Terminal
* ALT+3 Terminal
* ALT+4 Syslog file tailed contiously

Testing the daemon
==================

The daemon could be tested by simulating the requests, in this example 'C0A80014' is used for the pxelinux.cfg name which is hexidecimal for '192.168.0.20'. You will need to adjust this to the name of the pxe file generated with the 'seedbank pxe' command.

Generate the preseed file::

    wget "http://localhost:7467/seed/C0A80014" -q -O -

Download the Puppet manifests archive::

    wget "http://localhost:7467/manifests.tgz"

Test the start installation log message::

    wget "http://localhost:7467/pimp/C0A80014" -q -O -

Download the file overlay archive::

    wget "http://localhost:7467/overlay.tgz/C0A80014" -O overlay.tgz

Test the disable call ::

    wget "http://localhost:7467/disable/C0A80014" -q -O

Write a status file::

    wget "http://localhost:7467/status/C0A80014&state=done" -q -O

-----------------
Configure dnsmasq
-----------------

Dnsmasq is a fast, small and really easy to use caching DNS proxy and DHCP/TFTP server.

Installation
============

Install the dnsmasq package::

    sudo apt-get install dnsmasq

Configuration
=============

Here is a sample configuration which could be used with seedbank, it provides a caching DHCP, DNS and TFTP server::

    vi /etc/dnsmasq.d/seedbank

.. include:: manual/configs/dnsmasq/dnsmasq

The DNS server works with the */etc/hosts* file, it appends the configured domain to all entries without a domain::

    sudo vi /etc/hosts

    127.0.0.1       localhost
    192.168.20.1    seedbank001
    192.168.20.101  seed001
    192.168.20.102  seed002
    192.168.20.103  seed003

Restart dnsmasq::

   sudo /etc/init.d/dnsmasq restart

Resources
---------

Read */etc/dnsmasq.conf* for a good introduction to all features

    more /etc/dnsmasq.conf

Homepage

 * http://www.thekelleys.org.uk/dnsmasq/doc.html

--------------------------------
Create a Debian or Ubuntu mirror
--------------------------------

reprepro
========

This section is written for reprepro 4.2.0+. Reprepro is a nice tool to create Debian and or Ubuntu mirrors and your own apt repositories.

Installation
------------

Install reprepro:

    sudo apt-get --assume-yes install reprepro

GPG Configuration
-----------------

All packages repositories should be signed with a (your) GPG key. To make process this as painless as possible use *gpg-agent*.

Install the GNU GPG agent:

    sudo apt-get --assume-yes install gnupg-agent

List available GPG keys:

    sudo gpg --list-keys

Generate a new GPG key if there is no key availble:

    sudo gpg --gen-key

Add the following to *~/.profile* so gpg-agent will be invoked automatically when it is not running:

    vi ~/.profile

.. include:: manual/configs/gnugpg/.profile

Add the following line to your *.bash_profile*:

    vi ~/.bash_profile

.. include:: manual/configs/gnugpg/.bash_profile

Export the gpg key, replace 6A9E1B52 with the public ID of the key ID you just have generated:

    gpg --list-keys
    gpg --export -a 1ACC76B5 > repository.pub

Add the gpg key to the Debian or Ubuntu apt keyring:

    sudo apt-key add repository.pub

Gather various GPG keys
-----------------------

Get the GPG key for the Debian repository::

    cd /tmp
    wget http://ftp.us.debian.org/debian/dists/squeeze/Release
    wget http://ftp.us.debian.org/debian/dists/squeeze/Release.gpg
    gpg Release.gpg # enter: 'Release' as name of data file
    gpg --keyserver subkeys.pgp.net --search-keys "473041FA" # Enter '1'
    rm Release.gpg Release

Get the GPG key for the Ubuntu repository::

    cd /tmp
    wget http://mirrors.kernel.org/ubuntu/dists/natty/Release.gpg
    wget http://mirrors.kernel.org/ubuntu/dists/natty/Release
    gpg Release.gpg # enter: 'Release' as name of data file
    gpg --keyserver subkeys.pgp.net --search-keys 437D05B5 # Enter '1'
    gpg --keyserver subkeys.pgp.net --search-keys 55BE302B # Enter '1'
    rm Release.gpg Release

Run the following command to get the last 16 hex digits of the fingerprint::

    gpg --with-colons --list-key

    ::

    pub:-:4096:1:AED4B06F473041FA:2010-08-27:2018-03-05::-:Debian Archive Automatic Signing Key (6.0/squeeze) <ftpmaster@debian.org>::scSC:

In this case *AED4B06F473041FA* is the value to use for the reprepro *VerifyRelease* option in the conf/updates file(s).

Import the key to the GPG keyring and add it to the apt keyring::

    gpg --keyserver subkeys.pgp.net --recv AED4B06F473041FA
    gpg --export --armor AED4B06F473041FA | apt-key add -

Partial mirrors
---------------

It is possible to create partially mirrors with reprepro.

The trick is the *FilterFormula* parameter in the *conf/updates* file.

Example::

    FilterFormula: Priority (==required)

Create a Debian Squeeze and Debian Squeeze updates mirror
---------------------------------------------------------

Create the mirror directory including a conf directory, all mirror data will be stored here, be sure there is enough disk space available since mirrors take quite some disk space:

    mkdir -p /srv/repositories/debian/mirror/conf

Create the "conf/distributions" configuration file:

    vi /srv/repositories/debian/mirror/conf/distributions

.. include:: manual/configs/reprepro/debian/distributions

Create the "conf/updates" configuration file:

    vi /srv/repositories/debian/mirror/conf/updates

.. include:: manual/configs/reprepro/debian/updates

Sync or update the mirror:

    cd /srv/repositories/debian/mirror
    reprepro -V update

Create a Debian Squeeze security mirror
---------------------------------------

Create the security directory including a conf directory, all mirror data will be stored here, be sure there is enough disk space available since mirrors take quite some disk space:

    mkdir -p /srv/repositories/debian/security/conf

Create the "conf/distributions" configuration file:

    vi /srv/repositories/debian/security/conf/distributions

.. include:: manual/configs/reprepro/debian-security/distributions

Create the "conf/updates" configuration file:

    vi /srv/repositories/debian/security/conf/updates

.. include:: manual/configs/reprepro/debian-security/updates

Sync or update the mirror:

    cd /srv/repositories/debian/security
    reprepro -V update

Create a Debian Squeeze proposed updates mirror
-----------------------------------------------

Create the mirror directory including a conf directory, all mirror data will be stored here, be sure there is enough disk space available since mirrors take quite some disk space:

    mkdir -p /srv/repositories/debian/proposed-updates/conf

Create the "conf/distributions" configuration file:

    vi /srv/repositories/debian/proposed-updates/conf/distributions

.. include:: manual/configs/reprepro/debian-proposed/distributions

Create the "conf/updates" configuration file::

    vi /srv/repositories/debian/proposed-updates/conf/updates

.. include:: manual/configs/reprepro/debian-proposed/updates

Sync and update the mirror::

    cd /srv/repositories/debian/proposed-updates
    reprepro -V update

Create a Debian Squeeze backports mirror
----------------------------------------

Create the mirror directory including a conf directory, all mirror data will be stored here, be sure there is enough disk space available since mirrors take quite some disk space:

    mkdir -p /srv/repositories/debian/backports/conf

Create the "conf/distributions" configuration file:

    vi /srv/repositories/debian/backports/conf/distributions

.. include:: manual/configs/reprepro/debian-backports/distributions

Create the "conf/updates" configuration file:

    vi /srv/repositories/debian/backports/conf/updates

.. include:: manual/configs/reprepro/debian-backports/updates

Sync/Update the mirror:

    cd /srv/repositories/debian/backports
    reprepro -V update

Create a Ubuntu Natty mirror
----------------------------

Create a directory including a conf directory which will contain the mirror(s)::

    mkdir -p /srv/repositories/ubuntu/mirror/conf

Create the "conf/distributions" configuration file::

    vi /srv/repositories/ubuntu/mirror/conf/distributions

.. include:: manual/configs/reprepro/ubuntu/distributions

Create the "conf/updates" configuration file::

    vi /srv/repositories/ubuntu/mirror/conf/updates

.. include:: manual/configs/reprepro/ubuntu/updates

Sync or update the mirror:

    cd /srv/repositories/ubuntu/mirror
    reprepro -V update

Create a custom repository
--------------------------

Create the directory structure::

    sudo mkdir -p /srv/repositories/debian/custom/conf

Create the configuration file::

    sudo vi /srv/repositories/debian/custom/conf/distributions

::

    Origin: custom
    Label: Custom Debian Repository
    Codename: squeeze
    Architectures: i386 amd64 source
    Components: main
    Description: This repository contains custom Debian packages
    SignWith: your public gpgkey # (use gpg --list-keys to get the key)

Create the options file::

    vi /srv/repositories/debian/custom/conf/options

::

    basedir /srv/repositories/debian/custom

Add a package to the repository::

    cd /srv/repositories/debian/custom
    reprepro includedeb custom ~/seedbank_0.8.0_all.deb

Add the repository to the apt sources::

    sudo bash -c 'echo "deb http://192.168.0.1/debian/custom squeeze main" > /etc/apt/sources.list.d/custom.list'

Various reprepro commands
-------------------------

List all available packages for Debian Squeeze in the custom repository::

    reprepro -b /srv/repositories/debian/custom list squeeze
    cd /srv/repositories/debian/custom
    reprepro list squeeze

Add a Debian package to the custom repository::

    reprepro -Vb /srv/repositories/debian/custom includedeb squeeze ~/seedbank_0.8.0_all.deb

Remove the *seedbank* package from the custom repository::

    reprepro -Vb /srv/repositories/debian/custom remove squeeze seedbank

nginx
-----

The repository or repositories need to be accessible, one way to do is is via the very fast an lighweight web server Nginx.

Install Nginx::

    sudo apt-get install nginx

Make sure you have a CNAME configured in DNS which points to the *server_name* configuration directive.

Create a virtual host::

    sudo vi /etc/nginx/sites-available/packages

::

    server {

        listen      80;
        server_name packages.seedbank.local;
        autoindex   on;

        access_log /var/log/nginx/packages-access.log;
        error_log  /var/log/nginx/packages-error.log;

        location / {
            root /srv/repositories;
            index index.html;
        }

    }

Enable the virtual host::

    sudo ln -s /etc/nginx/sites-available/packages /etc/nginx/sites-enabled/
    sudo /etc/init.d/nginx restart

Resources
---------

Official

* http://mirrorer.alioth.debian.org/
* http://nginx.org/
* http://www.gnupg.org/

Lists with official Mirrors

* http://www.debian.org/mirror/list
* http://www.ubuntu.com/getubuntu/downloadmirrors

Reprepro

* http://davehall.com.au/blog/dave/2010/02/06/howto-setup-private-package-repository-reprepro-nginx
* http://www.jejik.com/articles/2006/09/setting_up_and_managing_an_apt_repository_with_reprepro/
* http://www.debianx.org/repo.html
* http://www.porcheron.info/setup-your-debianubuntu-repository-with-reprepro/
* http://www.lostwebsite.net/2008/10/partial-debian-mirrors/

GnuPG

* http://www.gentoo.org/doc/en/gnupg-user.xml
* http://irtfweb.ifa.hawaii.edu/~lockhart/gpg/gpg-cs.htm

Other mirror tools
==================

There is a handful of other mirror tools available, some to create full mirrors, some to create proxying mirrors.

If disk space/bandwith is an issue take a look to "apt-cacher", a really nice easy to setup proxy based mirror.
Unfortunately the last time I've checked it didn't like mixing distributions like Debian and Ubuntu together.

More information about some of the available tools

* http://help.ubuntu.com/community/Apt-Cacher-Server
* http://packages.debian.org/squeeze/apt-cacher
* http://packages.qa.debian.org/a/apt-cacher.html
* http://apt-proxy.sourceforge.net/
* http://apt-mirror.sourceforge.net/

---------------------
Third Party Resources
---------------------

* http://syslinux.zytor.com/wiki/
* http://wiki.debian.org/DebianInstaller/NetworkConsole
* http://wiki.debian.org/DebianInstaller/Remote
* http://wiki.debian.org/Bonding
* http://wiki.debian.org/DebianInstaller/NetbootFirmware

----------------
Network Services
----------------

Introduction
============

This section gives some small hints about setting up the required services, it is insufficient for a full configuration. It will probably never be sufficient because whole books about those topics are written. For more information see the resources section at the end of this guide.

Bind nameserver
===============

Install the TFTP service

.. code-block:: none

   sudo apt-get install bind9

Now you will need to configue DNS.

TFTPd HPA
==========

Install the TFTP service

.. code-block:: none

   sudo apt-get install tftpd-hpa

Enable the service and restart the tftpd-hpa daemon

.. code-block:: none

   sudo sed -i 's/RUN_DAEMON="no"/RUN_DAEMON="yes"/' /etc/default/tftpd-hpa
   sudo /etc/init.d/tftpd-hpa restart

ISC DHCP server
===============

Install the DHCP server

.. code-block:: none

    sudo apt-get install isc-dhcp-server

Enable the DHCP server

.. code-block:: none

    vi /etc/defaults/isc-dhcp-server

Configure the DHCP server

.. code-block:: none

    vi /etc/dhcp/dhcpd.conf

Example host configuration

.. code-block:: none

    host yield001.seedbank.local {
      fixed-address yield001.seedbank.local;
          option host-name yield001;
          hardware ethernet 66:66:66:66:66:66;
          next-server seedbank001.seedbank.local;
          option domain-name-servers 192.168.0.1, 192.168.0.2;
          filename "/pxelinux.0";
    }

Take care of the 'host-name option' otherwise Debian will misconfigure /etc/hosts.

Resources
---------

Various

 * http://wiki.debian.org/DHCP_Server
 * http://mindref.blogspot.com/2010/12/debian-dhcp-server.html

---------------
MAC OS X (Beta)
---------------

Introduction
============

Only ISO support has been tested on Mac OS X Lion.

NOTE: This section contains errors and is incomplete, feel free to improve ;)

Install Prerequisites
=====================

Install Git

.. code-block:: none

    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"
    brew update
    brew install git

Install the pyyaml package

.. code-block:: none

    sudo easy_install-2.7 pyyaml

Install cpio, gnutar and cdrtools via precompiled packages

.. code-block:: none

    cd /tmp
    curl -L -O http://infrastructureanywhere.com/downloads/osx/cdrtools-3.00.zip
    curl -L -O http://infrastructureanywhere.com/downloads/osx/cpio-2.11.zip
    curl -L -O http://infrastructureanywhere.com/downloads/osx/gnutar-1.26.zip
    unzip cdrtools-3.00.zip
    unzip cpio-2.11.zip
    unzip gnutar-1.26.zip
    sudo installer -pkg cdrtools-3.00.pkg -target /
    sudo installer -pkg cpio-2.11.pkg -target /
    sudo installer -pkg gnutar-1.26.pkg -target /

Clone the seedBank git repository and install seedBank

.. code-block:: none

    git clone https://github.com/jpoppe/seedBank.git
    cd seedBank
    sudo ./setup.py install

Install the additional tools vi MacPorts and build OS X packages
================================================================

Install MacPorts

.. code-block:: none

    curl -O https://distfiles.macports.org/MacPorts/MacPorts-2.0.4-10.7-Lion.dmg
    hdiutil mount MacPorts-2.0.4-10.7-Lion.dmg
    sudo installer -pkg /Volumes/MacPorts-2.0.4/MacPorts-2.0.4.pkg -target /
    hdiutil unmount /Volumes/MacPorts-2.0.4

Install cpio, gnutar and cdrtools via macports (will require xcode)

.. code-block:: none

    sudo port selfupdate
    sudo port install smake
    sudo port install cpio gnutar cdrtools

Build and zip OS X packages

.. code-block:: none

    port pkg cpio gnutar cdrtools

    cd ~/.macports/opt/local/var/macports/build/_opt_local_var_macports_sources_rsync.macports.org_release_tarballs_ports_archivers_cpio/cpio/work
    zip -r ~/cpio-2.11.zip cpio-2.11.pkg
    cd ~/.macports/opt/local/var/macports/build/_opt_local_var_macports_sources_rsync.macports.org_release_tarballs_ports_sysutils_cdrtools/cdrtools/work
    zip -r ~/cdrtools-3.00.zip cdrtools-3.00.pkg
    cd ~/.macports/opt/local/var/macports/build/_opt_local_var_macports_sources_rsync.macports.org_release_tarballs_ports_archivers_gnutar/gnutar/work
    zip -r ~/gnutar-1.26.zip gnutar-1.26.pkg

----------
IA Related
----------

Install VirtualBox on Mac OS X

.. code-block:: none

    curl -L -O http://download.virtualbox.org/virtualbox/4.1.8/VirtualBox-4.1.8-75467-OSX.dmg
    hdiutil mount VirtualBox-4.1.8-75467-OSX.dmg
    sudo installer -pkg /Volumes/VirtualBox/VirtualBox.mpkg -target /
    hdiutil unmount /Volumes/VirtualBox
