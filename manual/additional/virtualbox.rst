========================================
Deploy VirtualBox virtuals with seedbank
========================================

Notes
=====

After this section has been written Infrastructure Anywhere (:doc:`../addons/infrastructureanywhere/index` has been developed, if you are running a Linux system I recommend to dive into this instead of using Virtual Box.

Prerequisites
=============

A working Virtual Box setup with 2 nodes.

One node will be used as the seedbank server called *seedbank001* with 2 network interfaces, eth0 shoud be configured as a bridged interface and eth1 as an internal network interface.

The second node *seed001* should have one network interface for which the network interface should be configured as an internal network interface.

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
