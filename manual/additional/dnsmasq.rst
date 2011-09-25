=======
dnsmasq
=======

Dnsmasq is a fast, small and really easy to use caching DNS proxy and DHCP/TFTP server

Installation
============

Install the dnsmasq package
    sudo apt-get install dnsmasq

Configuration
=============

Here is a sample configuration which could be used with seedbank, it provides a caching DHCP, DNS and TFTP server.

.. code-block:: none

    vi /etc/dnsmasq.d/seedbank

.. literalinclude:: configs/dnsmasq

The DNS server works with the */etc/hosts* file, it appends the configured domain to all entries without a domain.

.. code-block:: none

    sudo vi /etc/hosts

.. code-block:: none

    127.0.0.1       localhost
    192.168.20.1    seedbank001
    192.168.20.101  seed001
    192.168.20.102  seed002    
    192.168.20.103  seed003

Restart dnsmasq

.. code-block:: none

   sudo /etc/init.d/dnsmasq restart

Resources
---------

Read */etc/dnsmasq.conf* for a good introduction to all features

.. code-block:: none

    more /etc/dnsmasq.conf

Homepage

 * http://www.thekelleys.org.uk/dnsmasq/doc.html
