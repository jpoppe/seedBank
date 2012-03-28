==========
QuickStart
==========

Introduction
============

This guide will help you to setup a seedBank server to do a fully unattended Debian Squeeze installation. It is easy adapt it to another Debian/Ubuntu release of your choice.

If you do not understand what a DHCP, DNS, TFTP server is then this guide is probably not for you. The concept of unattended/network installations seems to be pretty easy, but it is not. Many requirements needs to be fullfilled, the setup is sensitive and needs to be 'exact'.

seedBank aims to simplify this process as much as possible but still stay a powerfull tool. If you don't have the knowledge yet but still want to do those cool remote unatttended installations start reading on the net about those subjects. With some patience and practice it is definately possible, in the end it is no rocket science ;)

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
 * DNS Server (You could also use '/etc/hosts' (on the seedBank server) or use MAC address based installations)
 * Custom Debian/Ubuntu mirror(s) (see :doc:`../additional/mirrors` for instructions)

Any DNS, TFTP or DHCP server should work if configured properly. For an easy lightweight all in one solution you could use dnsmasq, see :doc:`../additional/dnsmasq` for more information.

I also recommend to gather some knowledge about the Debian preseed system, the predifined preseed files in '/etc/seedbank/seeds' should be enough to start with but to be able to use the full potential of seedBank some knowledge here is mandatory.

Installation
============

This section will describe how to install seedBank on seedbank001.intern.local

Install seedBank on Debian or Ubuntu without a repository

.. code-block:: none

    wget http://www.infrastructureanywhere.com/seedbank_2.0.0rc5_all.deb
    sudo dpkg -i seedbank_2.0.0rc5_all.deb
    sudo apt-get -f install

Install seedBank from a Debian or Ubuntu repository

.. code-block:: none

    sudo apt-get install seedbank

Install seedBank manually this will probably require more manual steps (like creating an init script) which won't be covered in this manual.

.. code-block:: none

    sudo python setup.py install

Configure default settings
==========================

seedBank configuration is in the YAML format. It's a wise idea to make a backup of the configuration before you start. I recommend to scroll through the configuration files in the '/etc/seedbank' directory so you will get a feeling about the possibilities.

Create a backup of the current seedBank configuration

.. code-block:: none

    sudo cp -r /etc/seedbank{,-org}

Edit the settings.yaml file, replace the IP address of the 'seed_host' variable with the IP address or fully qualified domain name of the server which you are running seedBank from

.. code-block:: none

    sudo vi /etc/seedbank/settings.yaml

You probably also want to customize the 'variables.yaml' configuration file. An explanation of the settings is described in this file.

.. code-block:: none

    sudo vi /etc/seedbank/conf.d/variables.yaml

After editing the settings.yaml file the seedBank daemon needs to be restarted so it will read the new settings.

.. code-block:: none

    sudo /etc/init.d/seedbank restart

Get the netboot image and syslinux files
========================================

The "seedbank manage" command is used for downloading and preparing the Debian Squeeze netboot image.

List all available netboot distributions

.. code-block:: none

    seedbank list -n

Download and install the required syslinux files to */var/lib/tftpboot* (Only need to be done once)

.. code-block:: none

    sudo seedbank manage -s

Download the Debian Squeeze netboot image tar archive and extract it to the right place (Only need to be done once)

.. code-block:: none

    sudo seedbank manage -n debian-squeeze-amd64

Generate the PXE file with seedBank
===================================

Run the following command on the seedBank server after reading the explanation below

.. code-block:: none

    sudo seedbank pxe -a 1disk_sd_one_partition seednode001.intern.local debian-squeeze-i386

Explanation:

This command will prepare everything for an automated install of a client (seednode001.intern.local).

The -a option specifies an additional seed file which will be appended at the end of the chosen preseed file, disk recipes are also preseed files so this will use the disk recipe which is located at */etc/seedbank/seeds/1disk_sd_one_partition.seed*.

NOTE: seedBank will automatically determine the distribution (Squeeze in this example). And it will look for a preseed file named after the chosen distribution

The seed file which will be used is chosen automatically, it takes the second part of the chosen distribution, so in this case the second part of *debian-squeeze-i386* is squeeze. seedBank will now use automatically */etc/seedbank/seeds/squeeze.seed* as the main preseed file. This behaviour can be overridden with the -s (--seed) option. So if you want to use another main preseed file, for example seednode001.seed instead of squeeze.seed run the following command

.. code-block:: none

    sudo seedbank pxe -a 1disk_sd_one_partition -s seednode001 seednode001.intern.local debian-squeeze-amd64

The seedBank command will generate */var/lib/tftpboot/pxelinux.cfg/C0A80014*. The filename is actually the IP address converted to hexidecimal, 192.168.0.20 in hexidecimal is C0A80014. This file is a PXE boot file which contains information which is used by the node as soon it boots via PXE. 

Take a look to the generated PXE file

.. code-block:: none

    cat /var/lib/tftpboot/pxelinux.cfg/C0A80014

Configure DHCP
==============

Configure the DHCP server so the seednode001 node will get the correct IP address assigned (in this example: 192.168.0.20). See :doc:`../additional/networkservices` for instructions

Boot the seedBank node
======================

Now cross your fingers and boot the 'seednode001.intern.local' node. If everything went right you should see the Debian installer doing his job fully automated, congratiulations! If not there could be many reasons, don't give up yet! See the troubleshooting section for information.

Advanced Example 1
==================

Install an Ubuntu Precise Pangolin node, copy a custom file overlay over the file system at the end of the installation, and use custom variables in the templates, run a standalone Puppet manifest at the end of the first boot of the machine. We will call the node 'ubuntu001.intern.local'.

Download the Ubuntu Precise Pangolin netboot image tar archive and extract it to the right place (Only need to be done once)

.. code-block:: none

    sudo seedbank manage -n ubuntu-precise-amd64

The following steps will be done by downloading a netboot image and when the default configuration is used:
- Check if the netboot image archive is already on the system (/var/cache/seedbank/archives/ubuntu-precise-amd64/netboot.tar.gz)
- If not it will download the netboot image archive to '/var/cache/seedbank/archives/ubuntu-precise-amd64/netboot.tar.gz'
- Extract the netboot image archive to '/tmp/seedbank/manage'
- Copy 'linux' and the 'initrd.gz' image to '/var/lib/tftpboot/seedbank/ubuntu-precise-amd64'
- Remove the temporary files

Create a custom file overlay with a custom script which will be run once after the installation

.. code-block:: none

    sudo mkdir -p /etc/seedbank/overlays/custom_overlay/etc/runonce.d
    echo "touch /seedbank_custom_overlay_test" > /etc/seedbank/overlays/custom_overlay/etc/runonce.d/custom_overlay_test.enabled
    echo "${fqdn}" > /etc/seedbank/overlays/custom_overlay/another_custom_overlay_test.sb_template
    echo 'this is a static file' > /etc/seedbank/overlays/custom_overlay/the_static_file_custom_overlay_test

To customize file permissions for a custom file overlay you can generate a permissions file which will be applied at the end of an installation

.. code-block:: none

    sudo seedbank manage -o custom_overlay

Now you can customize the generated permissions file, see the permissions file for an explanation about how to customize it.

.. code-block:: none

    sudo vi /etc/seedbank/overlays/custom_overlay.permissions

Since we have downloaded the required files and have the custom file overlay in place we can enable the target node for installation.

.. code-block:: none

    sudo seedbank pxe -m  -o custom_overlay -a 1disk_sd_one_partition -p example -v custom custom_variable ubuntu001.intern.local ubuntu-precise-amd64

Explanation of the above command

- sudo -> become root so you are allowed to write files in the tftpboot directory
- -m -> mac address of the machine to be installed, since a mac address will be specified there is no need of a DNS entry for ubuntu001.intern.local
- pxe -> the seedBank command to run
- -o custom_overlay -> specify the custom overlay directory you want to copy over the file system
- -a 1disk_sd_one_partition -> specify the additional seed file to append to the main seed file (Since we did not specify the main seed file with the -s (--seed) option seedbank will automatically use the preseed file named to the distribution we want to install, in this caes it will use precise.seed)
- -p example -> run the example Puppet Manifest (/etc/seedbank/manifests/example.pp) during the first boot after the installation.
- -v specify additional variables which will be stored in the generated pxelinux configuration
- ubuntu001.intern.local -> the fully qualified domain name of the node to install
- ubuntu-precise-amd64 -> the release to install

Advanced Example 2
==================

Describe the use of config overrides.


Where to go from here?
======================

seedBank has many more features then described in this quickstart guide. Scroll through the seedBank documentation to learn about the more advanced features. Also check the links section for more general information about (unattended) network installs.
