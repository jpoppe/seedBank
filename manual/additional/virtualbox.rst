========================================
Deploy VirtualBox virtuals with seedbank
========================================

Notes
=====

After this section has been written Infrastructure Anywhere (:doc:`../addons/infrastructureanywhere/index` has been developed, if you are running a Linux system I recommend to dive into this instead of using Virtual Box.

Prerequisites
=============

Two virtual machines

One node will be used as the seedbank server called *seedbank001* with 2 network interfaces, eth0 shoud be configured as a bridged interface and eth1 as an internal network interface.

The second node *seed001* should have one network interface for which the network interface should be configured as an internal network interface.

VirtualBox on Ubuntu
====================

VirtualBox Installation
-----------------------

Add the VirtualBox repository to the "apt sources"

.. code-block:: none

    sudo sh -c "echo 'deb http://download.virtualbox.org/virtualbox/debian oneiric contrib' > /etc/apt/sources.list.d/virtualbox.list"

Add the apt key to the keyring

.. code-block:: none

    wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc -O- | sudo apt-key add -

Update the package list and install VirtualBox

.. code-block:: none

    sudo apt-get update
    sudo apt-get install virtualbox-4.1 dkms

Install the VirtualBox extensions (Optional)
--------------------------------------------

Download and install the VirtualBox extensions

.. code-block:: none

    cd /tmp
    wget http://download.virtualbox.org/virtualbox/4.1.8/Oracle_VM_VirtualBox_Extension_Pack-4.1.8-75467.vbox-extpack
    sudo VBoxManage extpack install Oracle_VM_VirtualBox_Extension_Pack-4.1.4-74291.vbox-extpack

Configure the VirtualBox web server (Optional)
----------------------------------------------

The VirtualBox web server provides an API which can be used remotely

Edit the VirtualBox defaults, be sure at least the following two lines are in place

.. code-block:: none

    sudo vi /etc/defaults/virtualbox

.. code-block:: none
    
    VBOXUSER=vbox
    VBOXWEB_HOST=localhost

Start the VirtualBox web service

.. code-block:: none

    sudo /etc/init.d/vboxweb-service start

Make the VirtualBox web server start automatically

.. code-block:: none

    sudo update-rc.d vboxweb-service defaults

Download and install the VirtualBox SDK
---------------------------------------

Download the SDK zip archive and extract it

.. code-block:: none

    cd
    wget http://download.virtualbox.org/virtualbox/4.1.8/VirtualBoxSDK-4.1.8-75467.zip
    unzip VirtualBoxSDK-4.1.8-75467.zip

Install the SDK

.. code-block:: none

    cd sdk/installer
    sudo -s
    export VBOX_INSTALL_PATH=/usr/lib/virtualbox
    python vboxapisetup.py install
    exit

Share the network
-----------------

Paste the following in */etc/rc.local* to nat everything which comes from eth0

.. code-block:: none

    sudo vi /etc/rc.local

.. code-block:: none

    echo "1" > /proc/sys/net/ipv4/ip_forward
    iptables -F
    iptables -t nat -F
    iptables -I FORWARD -j ACCEPT
    iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE

Set up  a seedbank server in virtualbox
=======================================

Get a Debian Squeeze *netinstall* ISO

.. code-block:: none

    mkdir ~/ISOs
    cd ~/ISOs
    wget http://cdimage.debian.org/debian-cd/6.0.1a/amd64/iso-cd/debian-6.0.1a-amd64-netinst.iso    

Create the seedbank server in VirtualBox

.. code-block:: none

    VBoxManage createvm -name "seedbank" --ostype "Debian_64" -register
    VBoxManage modifyvm "seedbank" --memory 512 --acpi on --nic1 hostonly
    VBoxManage modifyvm "seedbank" --hostonlyadapter1 vboxnet0
    VBoxManage modifyvm "seedbank" --hostonlyadapter2 vboxnet0
    VBoxManage modifyvm "seedbank" --nic1 bridged --bridgeadapter1 eth0
    VBoxManage modifyvm "seedbank" --nic2 intnet
    VBoxManage createvdi -filename ~/.VirtualBox/HardDisks/seedbank.vdi -size 4096 --variant Standard
    VBoxManage storagectl seedbank --name sata0 --add sata
    VBoxManage storageattach seedbank --storagectl sata0 --port 0 --device 0 --type hdd --medium ~/.VirtualBox/HardDisks/seedbank.vdi
    VBoxManage storagectl seedbank --name IDE0 --add ide --controller PIIX4
    #VBoxManage storageattach seedbank --storagectl IDE0 --port 0 --device 0 --type dvddrive --medium /usr/share/virtualbox/VBoxGuestAdditions.iso
    VBoxManage storageattach seedbank --storagectl IDE0 --port 0 --device 0 --type dvddrive --medium ~/ISOs/seedbank_auto_debian_squeeze.iso

Show information about the virtual, start the virtual headless and connect to it

.. code-block:: none

    VBoxHeadless -startvm seedbank
    rdesktop localhost

Remove the Virtual

.. code-block:: none

    VBoxManage controlvm "seedbank" poweroff
    VBoxManage unregistervm "seedbank" --delete 

Additional commands

.. code-block:: none

    VBoxManage showvminfo seedbank
    VBoxManage controlvm seedbank poweroff
    VBoxManage controlvm seedbank acpipowerbutton
    VBoxManage modifyvm seedbank --boot1 dvd
