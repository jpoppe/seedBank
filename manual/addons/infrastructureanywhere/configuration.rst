==============
Configuring IA
==============

IA comes shipped with a set of configuration knobs, which can be overridden in configuration files. This document explains all these knobs and shows you how to override them.

------------------------
Configuration Parameters
------------------------

+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| Field           | Type    | Default                                                  | Description                                   |
+=================+=========+==========================================================+===============================================+
| confirm         | boolean | False                                                    | Confirm each major step within the script     |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| connect         | string  | <internal>                                               | Which libvirt instance to connect to. If this |
|                 |         |                                                          | is left empty, an internal variable will be   |
|                 |         |                                                          | used to select the correct host.              |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| cpu_type        | string  | Nehalem                                                  | CPU type to use for KVM hosts                 |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| disk_size       | integer | 3                                                        | Disk size in GB for deployed hosts            |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| dns_domain      | string  | a.c.m.e                                                  | DNS domain to place hosts in                  |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| ext_net         | string  | default                                                  | Name of the external (NAT) KVM network        |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| git_dir         | string  | ~/git                                                    | Location of the directory where you store     |
|                 |         |                                                          | your git repositories                         |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| git_repo        | string  | ecg-puppet-staging                                       | Name of the puppet GIT repository             |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| git_target      | string  | /tmp/chicken/acmefactory                                 | Where to store the puppet GIT repository      |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| home_dir        | string  | ~                                                        | Location of your home directory               |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| int_net         | string  | internal                                                 | Name of the internal (private) KVM network    |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| iso_url         | string  | http://cdimage.debian.org/debian-cd/current/amd64/iso-cd | Where to fetch the debian netinst iso from    |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| os_type         | string  | linux                                                    | OS type for deployed hosts                    |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| os_variant      | string  | debiansqueeze                                            | OS variant for deployed hosts                 |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| overlord        | list    | [192.168.122.2]                                          | List of overlords to use                      |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| platform_type   | string  | libvirt                                                  | Virtualisation platform to use. For now, only |
|                 |         |                                                          | libvirt is supported.                         |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| ram             | integer | 256                                                      | Amount of ram to allocate to deployed hosts   |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| repository      | string  | 192.168.122.1                                            | IP/FQDN of Debian repository to use           |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| seedbank        | string  | 192.168.122.2                                            | IP/FQDN of host where seedBank runs on        |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| ssh             | string  | /usr/bin/ssh                                             | Path to (custom) ssh                          |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| storage         | string  | default                                                  | Name of the storage pool to use               |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| storage_dir     | string  | /var/lib/libvirt/images                                  | Path to the libvirt images directory          |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| storage_mode    | string  | 0770                                                     | Filesystem permissions to use for creation    |
|                 |         |                                                          | of storage pools                              |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| storage_owner   | string  | libvirt-qemu                                             | Owner of the storage pools                    |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| storage_pool    | string  | acmefactory                                              | Name of the storage pool to use               |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| storage_type    | string  | qcow2                                                    | Storage pool type to use, can be qcow2 or     |
|                 |         |                                                          | LVM. Also see bugs_                           |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| use_wmctl       | string  | True                                                     | Use wmctl for window placement                |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| vcpus           | integer | 1                                                        | amount of cpu's to allocate to deployed hosts |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| volumegroup     | string  | acmefactory                                              | Name of the LVM volume group to use           |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| work_dir_local  | string  | /tmp/chicken/local                                       | Local work directory                          |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| work_dir_remote | string  | /tmp/chicken/remote                                      | Remote work directory                         |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+
| work_dir        | string  | /tmp/chicken                                             | Base work directory                           |
+-----------------+---------+----------------------------------------------------------+-----------------------------------------------+

.. _bugs: bugs.html

-----------------------
Overriding the defaults
-----------------------

You will want to override the defaults to customize IA to your environment. All variables are pushed into env within the fabric script, so you can use fabric configuration files to override this. These configuration files can be passed to fabric using the -c flag. Below you can find a couple of examples using this feature:

Define a QCOW2 based setup, using 'nat' and 'private' as libvirt networks and stop using wmctl:

.. code-block:: none

    ext_net      = nat
    int_net      = private
    use_wmctl    = False

Define a LVM based setup on a remote libvirt/kvm host, and specify a custom domain:

.. code-block:: none

    connect      = qemu+ssh://root@remote/system
    storage_type = lvm
    volumegroup  = lro

----------------------
Multiuser environments
----------------------

If you want to use a single libvirt system to support multiple users, there are a couple of settings you need to override per user. First, you'll need a custom domain for each user. This prevents IA from destroying the VM's of other users, since this is done on a per-domain basis. Second, you'll need to specify a custom storage_pool for each user. Assuming Alice and Bob are both using the same libvirt system, you'll need two configuration files:

.. code-block:: none

    dns_domain   = alice.some.domain
    storage_pool = alice

.. code-block:: none

    dns_domain   = bob.some.domain
    storage_pool = bob

If you want to use LVM, you'll need to create a volumegroup for each user. See :doc:`installation` for more details.
