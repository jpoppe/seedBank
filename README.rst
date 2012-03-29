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

License
=======
seedBank has been released under the Apache 2.0 license

Copyright 2009-2012 (c) Jasper Poppe <jpoppe@ebay.com>

Disclaimer
==========

seedBank does delete files, directories, partitions, whole systems, etc. so be REALLY careful when
you configure any paths! 
The author will not be responsible for any loss of data or system corruption. seedBank is a tool
which is able to create fully unattended installations so also be REALLY CAREFUL and do not
wipe a wrong system.

Introduction
============

Features
--------

- support for Debian and Ubuntu
- automated setup of Debian and Ubuntu PXE netboot images
- override most settings from the command line of via config override files
- support for custom enable and disable hooks
- support for running standalone Puppet manifests after an installation
- support for templated file overlays
- Debian non free firmware integration support
- and more

Requirements
------------

Python version 2.6 or 2.7
Properly configured DHCP server
Properly configured DNS Server (hosts file will also work)
Properly configured TFTP Server
A Debian or Ubuntu repository

Contributors
------------
- Martin Seener
- M.D. Klapdijk

Thanks to
=========

The Debian team for making all of this possible!
