=====================
seedBank Introduction
=====================

seedBank is a simple and flexible tool to manage unattended Debian and Ubuntu netboot installations. It is based on Debian preseed files, so it will provide the cleanest Debian installations possible by just using the standard Debian tools. Since version 2.0.0 it also has support for modifying installer ISOs so you could generate ISO's which are able to do unattended installations.

You could see seedBank as a lightweight alternative to FAI_ (Fully Automatic Installation) or Cobbler_, but much simpler and less bloated. seedBank is focused on one task, which is installing systems as easy, quick and clean as possible. Configuration tools like Puppet or Chef can take it over and configure the system after the installation has been completed.

.. _FAI: http://fai-project.org/
.. _Cobbler: https://fedorahosted.org/cobbler/

seedBank 'installs' are done via Debian or Ubuntu preseed files. Seeding is an important part of the Debian system and is basically used to configure anything. Preseed files are available for a long time but they are hard to manage and not flexible. This is where seedBank comes as the helping hand.

seedBank development started in August 2009 and has been open sourced to the world at PuppetConf 2011 Portland.

Media
=====

* Slides talk @ PuppetConf 2011: http://www.infrastructureanywhere.com/puppetconf2011_small.pdf
* Talk about seedBank 1.0 and Infrastructure Anyhwerere @ PuppetConf 2011: http://youtu.be/cjPjiHcc5rw

Resources
=========

* Homepage: http://www.infrastructureanywhere.com
* Mailing List: https://groups.google.com/group/infrastructureanywhere
* Changelog: https://github.com/jpoppe/seedBank/blob/master/CHANGES.txt
* GitHub: http://github.com/jpoppe
* Freshmeat: http://freshmeat.net/projects/seedbank
* Documentation: http://www.infrastructureanywhere.com/documentation
* Twitter: http://twitter.com/infraanywhere
* XING: https://www.xing.com/communities/groups/infrastructure-anywhere-strich-seedbank-05ad-1008537

Features
========

- support for the most recent releases of Debian and Ubuntu
- as clean and as simple as possible
- PXE netboot installation management
- create unattended installation ISOs
- no need for NFS mounts
- seedBank runs on Mac OS X (Only ISO support has been tested on Lion)
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

* Python version 2.6 or 2.7
* Properly configured DHCP server
* Properly configured DNS Server (hosts file will also work)
* Properly configured TFTP Server
* Access to Debian or Ubuntu repository

License
=======

seedBank has been released under the Apache 2.0 license

Copyright 2009-2015 (c) Jasper Poppe <jgpoppe@gmail.com>

Disclaimer
==========

seedBank does delete files, directories, partitions, whole systems, etc. so be REALLY careful when
you configure any paths, especially the temp path!
The author will not be responsible for any loss of data or system corruption. seedBank is a tool
which is able to create fully unattended installations so also be REALLY CAREFUL and do not
wipe the wrong system.

Contributors
============

- Martin Seener <martin[at]seener[dot]de>
- Marcel Klapwijk
- Glenn Aaldering

Thanks to
=========

The Debian team for making all of this possible!
