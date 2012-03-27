==========
QuickStart
==========

Introduction
============

This guide will help you to setup a seedBank server to do a fully unattended Debian Squeeze installation. It is easy adapt it to another Debian/Ubuntu release of your choice.

If you do not understand what a DHCP, DNS, TFTP server is then this guide is probably not for you. The concept of unattended/network installations seems to be pretty easy, but it is not. Many many requirements needs to be fullfilled, the total setup is sensitive and needs to be 'exact'.

seedBank aims to make this process easy but still powerfull. If you don't have the knowledge yet but still want to do those cool remote unatttended installations start reading on the net about the above subjects. With some patience and practice it is definately possible, in the end it is no rocket science ;)

It is assumed you have the following network topology:

seedBank server which will also run the DHCP, TFTP and DNS services (This should be a Debian or Ubuntu server with at least Python 2.5 installed):

.. code-block:: none

    Hostname: seedbank001.intern.local
    IP Address: 192.168.0.1

seedBank client which we are going to install:

.. code-block:: none

    Hostname: seednode001.intern.local
    IP Address: 192.168.0.20

Prerequisites
=============

To be able to use seedBank you will need to have the following components running
 * A connection to the internet (for downloading the netboot and installation files) for the seedBank server.
 * TFTP Server
 * DHCP Server
 * An additional host/virtual host for installing which is able to boot via PXE

Optional but recommended
 * DNS Server (You could also use /etc/hosts (on the seedBank server) or use MAC address based installations)
 * Custom Debian/Ubuntu mirror(s) (see :doc:`../additional/mirrors` for instructions)

Any DNS, TFTP or DHCP server should work if configured properly. For an easy lightweight all in one solution you could use dnsmasq, see :doc:`../additional/dnsmasq` for more information.

I also strongly recommend to gather some knowledge about the Debian seed system, all predifined seed files/recipes should be enough to start with but to be able to use the full potential of seedBank some knowledge here is mandatory.

Installation
============

This section will describe how to install seedBank on seedbank001.intern.local

Install seedBank from a Debian or Ubuntu repository

.. code-block:: none

    sudo apt-get install seedbank

Install seedBank on Debian or Ubuntu without a repository

.. code-block:: none

    wget http://www.infrastructureanywhere.com/seedbank_2.0.0rc5_all.deb
    sudo dpkg -i seedbank_2.0.0rc5_all.deb
    sudo apt-get -f install

Install seedBank manually (this will require more manual steps which won't be covered here)

.. code-block:: none

    sudo python setup.py install

Configure default settings
==========================

seedBank configuration is in the YAML format. It's a wise idea to make a backup of the configuration before you start.

Create a backup of the current seedBank configuration

.. code-block:: none

    sudo cp -r /etc/seedbank{,-org}

Edit the settings.yaml file, replace the IP address of the 'seed_host' variable with the IP address or fully qualified domain name of the server which you are running seedBank from

.. code-block:: none

    sudo vi /etc/seedbank/settings.yaml

After editing the settings.yaml file the seedBank daemon needs to be resarted to use the new settings.

.. code-block:: none

    sudo /etc/init.d/seedbank restart

Get the netboot image and syslinux files
========================================

Run "seedbank manage" for downloading and preparing the Debian Squeeze netboot image.

List all available netboot distributions

.. code-block:: none

    seedbank list -n

Download and install the required syslinux files to */var/lib/tftpboot*

.. code-block:: none

    sudo seedbank manage -s

Download the Debian Squeeze netboot image tar archive and extract it to the right place

.. code-block:: none

    sudo seedbank manage -n debian-squeeze-amd64

Generate the PXE file with seedBank
===================================

Run the following command on the seedBank server after reading the explanation below

.. code-block:: none

    sudo seedbank net -a 1disk_sd_one_partition seednode001.intern.local debian-squeeze-i386

Explanation:

This command will prepare everything for an automated install of a client (seednode001).

The -a option specifies a recipe to append at the end of the chosen seed file, in the default seedBank setup recipes are used for partitioning the hard disk, so this will use the disk recipe which is located at */etc/seedbank/recipes/desktop*.

The seed file which will be used is chosen automatically, it takes the second part of the chosen distribution, so in this case the second part of *debian-squeeze-i386* is squeeze. seedBank will now use automatically */etc/seedbank/seeds/squeeze.seed* as seed file. This can be overridden with the -s option.

The argument (debian-squeeze-i386) is the distribution which will be used to install.

The seedBank command will now generate */var/lib/tftpboot/pxelinux.cfg/C0A80014*. The filename is actually the IP addres converted to hexidecimal, 192.168.0.20 in hexidecimal is C0A80014. This file is a PXE boot file which contains information which is used by the node as soon it boots via PXE. 

Take a look to the just generated PXE file

.. code-block:: none

    cat /var/lib/tftpboot/pxelinux.cfg/C0A80014


Configure DHCP
==============

Configure the DHCP server so the seednode001 will get the correct IP address assigned (here: 192.168.0.20). See :doc:`../additional/networkservices` for instructions

Boot the seedBank node
======================

Now cross your fingers and boot the seedBank node. If everything went right you should see the Debian installer doing his job fully automated, congratiulations! If not there could be many causes. See the troubleshooting section for some ideas.

Where to go from here?
======================

seedBank has many more features then described in this quickstart guide. Scroll through the seedBank documentation to learn about the more advanced features. Also check the links section for more general information about (unattended) network installs and all the stuff around it.
