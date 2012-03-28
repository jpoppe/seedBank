========
Overview
========

seedBank is a simple tool to manage Debian and Ubuntu netboot installations. It is based on Debian preseed files, so it will provide the cleanest Debian installations possible by just using the standard Debian tools.

The development of seedBank started in August 2009 and it is since Septemer 23rd available for the public.

seedBank has been rewritten for version 2.0. Configuration and code have been simplified a lot also support for creating unattended Debian and Ubuntu ISOs have been added.

Features
========

- netboot installation management
- clean and simple
- no need for NFS mounts
- stores data which is needed by the installer in the pxelinux.cfg files, so no database backend!
- many configuration possibilities
- support for the latest Debian and Ubuntu versions out of the box
- includes carefully hand crafted ready to use templated preseed files
- integrates Debian non free firmware files into the netboot image
- automated setup of debian/ubuntu pxe netboot images
- custom enable and disable hooks for easy integration with external tools
- support for serverless Puppet manifests which will be applied after an installation
- support for templated file overlays
- makes it easy to do installations over serial consoles
- supports configuration overrides
- support for generating unattended installation ISOs
- written in Python
- more..

- external nodes support

How does it work?
=================

seedBank based installations are done via Debian/Ubuntu preseed files. Those preseed files are part of the Debian installer and are available for quite some time. But they are pretty hard to manage and not flexible. This is where seedBank comes to be the helping hand. See the diagram for a basic overview.

Links
=====

Alternatives
 * http://fai-project.org/
 * http://fedorahosted.org/cobbler/

Resources
 * http://syslinux.zytor.com/wiki/
 * http://wiki.debian.org/DebianInstaller/NetworkConsole
 * http://wiki.debian.org/DebianInstaller/Remote
 * http://wiki.debian.org/Bonding
 * http://wiki.debian.org/DebianInstaller/NetbootFirmware

Disclaimer
==========

seedBank does delete files, directories, partitions, whole systems, etc. so be REALLY careful when you configure any paths, especially the temp path!!!

The author will not be responsible for any loss of data or system corruption!
