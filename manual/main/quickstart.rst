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

Install seedBank from a Debian/Ubuntu repository

.. code-block:: none

    sudo apt-get install seedbank

Install seedBank in Debian/Ubuntu without a repository

.. code-block:: none

    sudo dpkg -i seedbank*.deb
    sudo apt-get -f install

Or install seedBank manually (this will need more manual steps which won't be covered here)

.. code-block:: none

    sudo python setup.py install

Configure default settings
==========================

The seedBank settings.py file is just a Python source file with dictionaries, so no errors are allowed. It's a wise idea to make a backup before you start editing the file.

Create a backup

.. code-block:: none

    sudo cp /etc/seedbank/settings.py{,-org}

Edit the settings.py file, please take some time to scroll through the file, since seedBank is using a lot of templating the possibilities are endless. I recommend to leave the default settings for now. If the seedBank server address is not 192.168.0.1 change it now.

.. code-block:: none

    sudo vi /etc/seedbank/settings.py

After editing the settings.py file the seedBank daemon needs to be resarted to use the new settings.

.. code-block:: none

    sudo /etc/init.d/seedbank restart

Get the netboot image and syslinux files
========================================

Run seedbank_setup for downloading and preparing the Debian Squeeze netboot image.

List all available distributions

.. code-block:: none

    seedbank_setup -l

Download and install the needed syslinux files to */var/lib/tftpboot*

.. code-block:: none

    sudo seedbank_setup -s

Download the Debian Squeeze netboot image

.. code-block:: none

    sudo seedbank_setup debian-squeeze-amd64

Generate the PXE file with seedBank
===================================

Run the following command on the seedBank server after reading the explanation below

.. code-block:: none

    sudo seedbank -H seednode001.intern.local -r default debian-squeeze-i386

Explanation:

This command will prepare everything for an automated install of a client (seednode001).

The -H option specfies you want to enable a host by hostname. seedBank will do a DNS lookup to get the IP address which in our case will be 192.168.0.20.

The -r option specifies a recipe to append at the end of the chosen seed file, in the default seedBank setup recipes are used for partitioning the hard disk, so this will use the disk recipe which is located at */etc/seedbank/recipes/desktop*.

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
