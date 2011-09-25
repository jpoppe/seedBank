========
seedbank
========

This section describes how to use seedBank, if this is the first time you will use seedBank please first read/modify /etc/seedbank/settings.py and the quick start guide.

Application Help
================

.. include:: help/seedbank

Options
=======

Arguments
=========

- The first argument should be a fully qualied domain name

- For the second argument one of the available releases should be used which can be listed by using the -l option

Host options
------------

There are 3 ways to specify a host

-H Specify a fully qualified hostname, when you use this option seedBank will do a DNS lookup for the IP address, so DNS needs to work properly, if DNS is not working or you do not want to use DNS you could also add a host definition to /etc/hosts

-i Specify an ip address, when you use this option seedBank will do a reverse DNS lookup for the fully qualified domain/hostname, so DNS needs to work properly, if DNS is not working or you do not want to use DNS you could also add a host definition to /etc/hosts

-e Specify a (fully qualified) host name which will be looked up via the external nodes script which is configured in settings.py

Overlay
-------

-o Specify an overlay, this is a directory with files and templates which will be copied over the filesystem at the end of the installation process

Custom Settings Override
------------------------

-c With this option you can override most settings on the fly from settings.py. This option can be invoked multiple times.

Seed
----

-s With this option you can override the default seed file which is used. (default is "distribution name.seed", so for example squeeze.seed)

Recipes
-------

-r Specify a recipe (A partial seed file which will be appended to the chosen seed file), it's recommended to use this for disk recipes. This option can be invoked multiple times.

Manifests
---------

-m Specify a Puppet manifest which should be run by Puppet after the first boot. This option can be invoked multiple times.

Examples
========

Prepare an installation for Debian Squeeze amd64 with the minimal required options (DNS should be configured properly).

.. code-block:: none

    seedbank -H minion001.a.c.m.e debian-squeeze-amd64

Prepare an installation for Ubuntu Natty with a custom disk layout, run the network manifest and override some settings from settings.py

.. code-block:: none

    seedbank -i 192.168.0.10 -r default -m network -c "settings_pxe:extra:console=ttyS0,115200n8 netcfg/dhcp_timeout=60 debian-installer/allow_unauthenticated=true" ubuntu-natty-amd64
