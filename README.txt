========
seedbank
========

seedbank is a small but very flexible system to manage Debian/Ubuntu unattended installations.

The development of seedbank is started in August 2009.

Disclaimer
==========

seedbank does delete files, directories, partitions, whole systems, etc. so be REALLY careful when
you configure any paths! 
The author will not be responsible for any loss of data or system corruption. seedbank is a tool
which is able to create fully unattended installations so also be REALLY CAREFULL to not
wipe a wrong system.

Introduction
============

Features
--------

- support for Debian and Ubuntu
- automated setup of debian/ubuntu pxe netboot images
- override any setting from settings.py on the command line
- support for custom enable / disable hooks
- support for running standolone puppet manifests
- support for templated file overlays
- external nodes support
- Debian non free firmware integration support
- much more

Requirements
------------

Python version 2.5 or higher
Properly configured DHCP server
Properly configured DNS Server (hosts file will also work)
Properly configured TFTP Server
wget (apt-get install wget)

DHCP, DNS and TFTP
==================

Dnsmasq
-------

Install dnsmasq
    sudo apt-get install dnsmasq

ISC dhcp server, bind and tftpd hpa
-----------------------------------

Install DNS, DHCP and TFTP server
   sudo apt-get install dhcp3-server bind9 tftpd-hpa

Enable and restart tftpd-hpa daemon
   sudo sed -i 's/RUN_DAEMON="no"/RUN_DAEMON="yes"/' /etc/default/tftpd-hpa
   sudo /etc/init.d/tftpd-hpa restart


Take care of the 'host-name option' otherwise Debian will misconfigure /etc/hosts.

Example DHCP host configuration
    host yield001.seedbank.local {
      fixed-address yield001.seedbank.local;
          option host-name yield001;
          hardware ethernet 66:66:66:66:66:66;
          next-server seedbank001.seedbank.local;
          option domain-name-servers 192.168.0.1, 192.168.0.2;
          filename "/pxelinux.0";
    }
    
Create custom mirrors
=====================

Caching Mirrors
---------------

Apt-cacher
    http://packages.debian.org/squeeze/apt-cacher

Full mirrors
------------

Reprepro
   sudo apt-get install reprepro

Links
=====

Resources
* http://syslinux.zytor.com/wiki/
* http://wiki.debian.org/DebianInstaller/NetworkConsole
* http://wiki.debian.org/DebianInstaller/Remote
* http://wiki.debian.org/Bonding
* http://wiki.debian.org/DebianInstaller/NetbootFirmware

Thanks to
=========

Guido for creating Python...
The Debian team for making all of this possible!
