================
Network Services
================

Introduction
============

This section gives some small hints about setting up the required services, it is insufficient for a full configuration. It will probably never be sufficient because whole books about those topics are written. For more information see the resources section at the end of this guide.

Bind nameserver
===============

Install the TFTP service

.. code-block:: none

   sudo apt-get install bind9

Now you will need to configue DNS.

TFTPd HPA
==========

Install the TFTP service

.. code-block:: none

   sudo apt-get install tftpd-hpa

Enable the service and restart the tftpd-hpa daemon

.. code-block:: none

   sudo sed -i 's/RUN_DAEMON="no"/RUN_DAEMON="yes"/' /etc/default/tftpd-hpa
   sudo /etc/init.d/tftpd-hpa restart

ISC DHCP server
===============

Install the DHCP server

.. code-block:: none

    sudo apt-get install isc-dhcp-server

Enable the DHCP server

.. code-block:: none

    vi /etc/defaults/isc-dhcp-server

Configure the DHCP server

.. code-block:: none

    vi /etc/dhcp/dhcpd.conf

Example host configuration

.. code-block:: none

    host yield001.seedbank.local {
      fixed-address yield001.seedbank.local;
          option host-name yield001;
          hardware ethernet 66:66:66:66:66:66;
          next-server seedbank001.seedbank.local;
          option domain-name-servers 192.168.0.1, 192.168.0.2;
          filename "/pxelinux.0";
    }

Take care of the 'host-name option' otherwise Debian will misconfigure /etc/hosts.

Resources
---------

Various

 * http://wiki.debian.org/DHCP_Server
 * http://mindref.blogspot.com/2010/12/debian-dhcp-server.html

