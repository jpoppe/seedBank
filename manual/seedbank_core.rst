========
seedBank
========

This section describes how to use the seedbank binary, if this is the first time you will use seedBank please first read/modify /etc/seedbank/settings.yaml, /etc/seedbank/system.yaml and read the quick start guide.

Main Application
================

.. include:: help/seedbank

List Command
============

List resources like netboot images, seed files, Puppet manifests, configuration overrides, file overlays, pxelinux.cfg files, netboot images and ISOs

Help Output
-----------

.. include:: help/seedbank_list

Net Command
===========

.. include:: help/seedbank_net

ISO Command
===========

.. include:: help/seedbank_iso

Manage Command
==============

.. include:: help/seedbank_manage

Examples
========

Download the syslinux archive and put the files required for a netboot installation in the right place. Download the Debian Squeeze AMD64 netboot image and put it in the right place

.. code-block:: none

    seedbank manage
    seedbank manage --syslinux

Prepare an installation for Debian Squeeze amd64 with the minimal required options (DNS should be configured properly since it will gather the IP address via a DNS lookup).

.. code-block:: none

    seedbank net minion001.a.c.m.e debian-squeeze-amd64

NOTE: if the default configuration (seed files) are used the installation will require user input for partitioning the disks, to do a fully unattended installation a disk recipe should be added to the command

.. code-block:: none

    seedbank net -s disk_one_partition minion001.a.c.m.e debian-squeeze-amd64

Prepare an installation for Ubuntu Precise with a custom disk layout, run the Puppet network manifest after the installation and specify some custom PXE variable which could be used in the file overlay templates

.. code-block:: none

    seedbank net -s one_partition -m network -o minion minion001.a.c.m.e ubuntu-natty-amd64
