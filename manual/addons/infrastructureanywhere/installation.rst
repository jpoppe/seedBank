==================
Installation of IA
==================

This document explains how to get IA configured so you can start rolling out your own infrastructure. This document will focus on the preparation of KVM. Partial VirtualBox and VMWare support is available, but thats out of the scope of this document. This document will assume you have a freshly installed Debian Squeeze system.

------------
Preparations
------------

First off, install the required packages. See :doc:`versions` for the required version numbers. You need to be root to perform these steps.

.. code-block:: none

    apt-get install qemu-kvm libvirt0 libvirt-bin virt-viewer virtinst bsdtar genisoimage

IA assumes you're running as a normal user. For this to work, you need to add your user to the libvirt and kvm groups:

.. code-block:: none

    adduser <yourusername> libvirt
    adduser <yourusername> kvm

Next, you need to fix the permissions of the images directory of libvirt, so you can write to it as a normal user:

.. code-block:: none

    chown libvirt-qemu:kvm /var/lib/libvirt/images
    chmod g+w /var/lib/libvirt/images

Since the fabric version that comes with Squeeze is quite old, it misses some needed features, so you'll need to either add the unstable repositories, or install fabric through setuptools.

To install fabric through the unstable repositories, perform the following steps:

.. code-block:: none

    echo "deb http://ftp.nl.debian.org/debian/ unstable main non-free contrib" >> /etc/apt/sources.list
    echo "APT::Default-Release 'squeeze';" >> /etc/apt/apt.conf.d/00pinning
    apt-get update
    apt-get -t unstable install fabric

To install fabric through python' setup tools, perform the following step:

.. code-block:: none

    apt-get install python-setuptools
    easy_install -U fabric

Fabric uses paramiko to perform operations over ssh. Unfortunately, this breaks if you want to use ProxyCommands. To fix this, you can use paraproxy, which has (somewhat limited) support for ProxyCommands. Since paraproxy isn't packaged, you'll need to use setuptools to install it:

.. code-block:: none

    easy_install paraproxy

You'll need to patch fabric to use paraproxy. You will need to do this everytime you install and/or upgrade fabric. Modify fabric/network.py as below:

.. code-block:: none

     16 try:
     17     import warnings
     18     warnings.simplefilter('ignore', DeprecationWarning)
     19     import paraproxy
     20     import paramiko as ssh
     21 except ImportError:
     22     try:
     23         import warnings
     24         warnings.simplefilter('ignore', DeprecationWarning)
     25         import paramiko as ssh
     26     except ImportError:
     27         abort("paramiko is a required module. Please install it:\n\t"
     28               "$ sudo easy_install paramiko")

---------------
Configuring LVM
---------------

If you want to use LVM as a storage backend, you'll need to install lvm, together with some sudo rules:

.. code-block:: none

    apt-get install lvm2

Add the following to lines to your sudoers file:

.. code-block:: none

    %libvirt ALL=(ALL) NOPASSWD: /sbin/vgcreate
    %libvirt ALL=(ALL) NOPASSWD: /sbin/lvcreate

When initializing a VG from within libvirt, it needs to be deactivated before you can use it. This means that you cannot use your existing VG. To workaround this, you can create a nested VG on top of your existing VG. The example below creates 'nestedvg' below 'parentvg':

.. code-block:: none

    lvcreate -L50G -n nestedvg parentvg
    vgcreate nestedvg /dev/parentvg/nestedvg

Make sure to name your volumegroup 'nestedvg' within your configuration.

--------------------------
Configuring KVM networking
--------------------------

IA needs two networks to work properly. You'll need one NAT'ted network, and one private network. IA also needs to have fixed ip addresses, so we need to configure them. In the IA source directory, there are two XML definitions which take care of this, but you'll need to install them by hand.

Start by copying the XML definitions to the libvirt config directory and autostarting them:

.. code-block:: none

    cd /path/to/acmefactory
    cp ingredients/libvirt/default.xml ingredients/libvirt/internal.xml /etc/libvirt/qemu/networks
    cd /etc/libvirt/qemu/networks/autostart
    ln -s ../\*.xml .

Unfortunately, libvirt does not cleanup it's networks during a restart, so a reboot is needed:

.. code-block:: none

    reboot

-------------------------------
Preparing your user environment
-------------------------------

Since fabric uses ssh to perform most of it's operations, using a ssh key is recommended. If you don't have a ssh key, create one:

.. code-block:: none

    ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa

You need to copy this key to the system(s) on which KVM runs, even if this is your local system:

.. code-block:: none

    ssh-copy-id localhost
    ssh-copy-id some.kvm.host

--------------------------
Setting up a debian mirror
--------------------------

If you do a lot of deployments, it's useful to setup a local debian mirror. Setting up a debian mirror can be done in two ways. Either you can run a complete mirror, which takes approximately 100GB of diskspace, or you can run a caching proxy.

`Setting up a local debian mirror`

See :doc:`../../additional/mirrors` for more information.

`Setting up a caching proxy`

You can also use apt-cacher-ng to act as a caching proxy. First, install apt-cacher-ng:

.. code-block:: none

    apt-get install apt-cacher-ng

Next, you need to add the debian-security repository. Edit /etc/apt-cacher-ng/acng.conf and add the following line:

.. code-block:: none

    Remap-debsec: file:deb_sec_mirrors /debian-security ; file:backends_debian_sec

You also need to add a file containing debian-security mirrors:

.. code-block:: none

    echo "http://ftp.nl.debian.org/debian-security" > /etc/apt-cacher-ng/backends_debian_sec
    ln -s /etc/apt-cacher-ng/backends_debian_sec /etc/apt-cacher-ng/deb_sec_mirrors

Restart apt-cacher-ng to make your changes take effect

.. code-block:: none

    /etc/init.d/apt-cacher-ng restart

`Serving a custom repository`

See :doc:`../../additional/mirrors` for more information.
