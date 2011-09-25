========
Overview
========

seedBank is a simple tool to manage and template Debian seed files. Since it is based on seed files it will provide the cleanest Debian installations possible by just using the standard Debian tools. seedBank has been written in Python.

The development of seedBank started in August 2009 and is since Septemer 23rth available for the public.

Features
========

- netboot files management
- support for the latest Debian and Ubuntu versions out of the box
- includes carefully hand crafted ready to use templated preseed files
- integrates Debian non free firmware to the netboot image
- automated setup of debian/ubuntu pxe netboot images
- custom enable and disable hooks for easy integration with external tools
- stand alone puppet manifests which will be applied after an installation
- support for templated file overlays
- external nodes support
- Debian non free firmware integration support
- integrates Debian non free firmware to the netboot image
- makes it easy to do installations over serial consoles
- more..

Links
=====

Resources
 * http://syslinux.zytor.com/wiki/
 * http://wiki.debian.org/DebianInstaller/NetworkConsole
 * http://wiki.debian.org/DebianInstaller/Remote
 * http://wiki.debian.org/Bonding
 * http://wiki.debian.org/DebianInstaller/NetbootFirmware

Alternatives
 * http://fai-project.org/
 * http://fedorahosted.org/cobbler/

Disclaimer
==========

seedBank does delete files, directories, partitions, whole systems, etc. so be REALLY careful when you configure any paths and think twice before you make any step!

The author will not be responsible for any loss of data or system corruption!
