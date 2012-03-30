========
seedBank
========

seedBank is a small but very flexible tool to manage Debian/Ubuntu unattended installations.

Development started in August 2009, seedbank has been open sourced at PuppetConf 2011 Portland

* Homepage: http://www.infrastructureanywhere.com
* Mailing List: https://groups.google.com/group/infrastructureanywhere
* Changelog: https://github.com/jpoppe/seedBank/blob/master/CHANGES.txt
* GitHub: http://github.com/jpoppe
* Freshmeat: http://freshmeat.net/projects/seedbank
* Documentation: http://www.infrastructureanywhere.com/documentation
* Twitter: http://twitter.com/infraanywhere

Media

* Talk about seedBank 1.0 @ PuppetConf: http://youtu.be/cjPjiHcc5rw
* Slides Talk PuppetConf: http://www.infrastructureanywhere.com/puppetconf2011_small.pdf

License
=======
seedBank has been released under the Apache 2.0 license

Copyright 2009-2012 (c) Jasper Poppe <jpoppe@ebay.com>

Disclaimer
==========

seedBank does delete files, directories, partitions, whole systems, etc. so be REALLY careful when
you configure any paths, especially the temp path!
The author will not be responsible for any loss of data or system corruption. seedBank is a tool
which is able to create fully unattended installations so also be REALLY CAREFUL and do not
wipe the wrong system.

Introduction
============

Overview
--------

seedBank is a simple tool to manage Debian and Ubuntu netboot installations. It is based on Debian preseed files, so it will provide the cleanest Debian installations possible by just using the standard Debian tools. Since version 2.0.0 it also has support for modifying installer ISOs so the installer can run unattended,

You could see it is a lightweight alternative to FAI (Fully Automatic Installation) or Cobbler, but much simpler and less bloated. seedBank is focused on one task and that is installing systems as clean as possible and let configuration tools like Puppet and Chef take it over after the installation. 

The development of seedBank started in August 2009 and it is since September 23rd available for the public.

How does it work?
-----------------

seedBank 'installations' are done via Debian or Ubuntu preseed files. Seeding is an important part of the Debian system and is basically used to configure anything. Preseed files are available for a long time but they are hard to manage and not flexible. This is where seedBank comes to be the helping hand.

Features
--------

- support for the most recent releases of Debian and Ubuntu
- clean and as simple as possible
- PXE netboot installation management
- no need for NFS mounts
- stores data which is needed by the installer in the pxelinux.cfg files, so no database backend!
- many configuration possibilities
- support for the latest Debian and Ubuntu versions out of the box
- includes carefully hand crafted ready to use templated preseed files
- integrates Debian non free firmware files into the netboot image
- automated setup of debian and ubuntu pxe netboot images
- custom enable and disable hooks for easy integration with external tools
- support for serverless Puppet manifests which will be applied after an installation
- support for templated file overlays
- makes it easy to do installations over serial consoles
- supports configuration overrides
- support for generating unattended installation ISOs
- written in Python
- and more..

Requirements
============

Python version 2.6 or 2.7
Properly configured DHCP server
Properly configured DNS Server (hosts file will also work)
Properly configured TFTP Server
A Debian or Ubuntu repository

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

Contributors
============

- Martin Seener
- Marcel Klapwijk

Thanks to
=========

The Debian team for making all of this possible!
