========
Using IA
========

Functions prefixed with an underscore are for use by IA internally.

--------------------
VM related functions
--------------------

+--------------------+------------------------------------------+--------------------------------------+
| function           | parameters                               | description                          |
+====================+==========================================+======================================+
| _overlord          | name, ip_address, ip_address2,           | Install a new overlord, using an ISO |
|                    | auto(False), repository(192.168.122.1),  |                                      |
|                    | puppet(True), snapshot(False)            |                                      |
+--------------------+------------------------------------------+--------------------------------------+
| _minion            | name, ip_address, domain(a.c.m.e),       | Install a new minion, using seedBank |
|                    | ram(512), disk_size(3), overlay(minion), |                                      |
|                    | type(debian-squeeze-amd64)               |                                      |
+--------------------+------------------------------------------+--------------------------------------+
| virt_connect       | name, script, snapshot(False)            | Start the VM, and reboot it when it  |
|                    |                                          | is done installing, working around   |
|                    |                                          | bugs within libvirt                  |
+--------------------+------------------------------------------+--------------------------------------+
| list_all_snapshots | None                                     | List all available snapshots         |
+--------------------+------------------------------------------+--------------------------------------+
| create_snapshot    | name(overlord001)                        | Create a new snapshot for the named  |
|                    |                                          | system                               |
+--------------------+------------------------------------------+--------------------------------------+
| restore_snapshot   | name, snapshot                           | Restore a snapshot for the named     |
|                    |                                          | system                               |
+--------------------+------------------------------------------+--------------------------------------+
| remove_snapshot    | name, snapshot                           | Remove a snapshot for the named      |
|                    |                                          | system                               |
+--------------------+------------------------------------------+--------------------------------------+
| remove             | name                                     | Remove the named host. Can support   |
|                    |                                          | case-insensitive regular expressions |
+--------------------+------------------------------------------+--------------------------------------+
| remove_all         | None                                     | Remove all hosts                     |
+--------------------+------------------------------------------+--------------------------------------+

-----------------
Generic functions
-----------------

+-------------------+---------------------------------------------+-------------------------------------+
| function          | parameters                                  | description                         |
+===================+=============================================+=====================================+
| sync              | name(overlord001), destination(/etc/puppet) | Rsync the puppet repository to the  |
|                   |                                             | named host                          |
+-------------------+---------------------------------------------+-------------------------------------+
| test              | name(overlord001), debug(False)             | Perform a sync() and run puppet on  |
|                   |                                             | the named system                    |
+-------------------+---------------------------------------------+-------------------------------------+
| bootstrap         | name(overlord001)                           | Copy the puppet repository to the   |
|                   |                                             | named system and perform a puppet   |
|                   |                                             | bootstrap                           |
+-------------------+---------------------------------------------+-------------------------------------+
| update_dns_domain | None                                        | Update the powerdns schema on the   |
|                   |                                             | overlord. See powerdns for details  |
+-------------------+---------------------------------------------+-------------------------------------+

------------------
Specific functions
------------------

+------------------+----------------------------+----------------------------------------------------+
| function         | parameters                 | description                                        |
+==================+============================+====================================================+
| overlord001      | ip_address(192.168.122.1), | Remove all nodes under the configured domain and   |
|                  | ip_address2(192.168.20.1)  | Roll-out overlord001, including puppet.            |
| overlord001_bare | ip_address(192.168.122.1), | Remove all nodes under the configured domain and   |
|                  | ip_address2(192.168.20.1), | roll-out overlord001, without puppet and create    |
|                  | puppet(True)               | a snapshot                                         |
+------------------+----------------------------+----------------------------------------------------+
| overlord002      | puppet(True)               | Remove and roll-out overlord002                    |
+------------------+----------------------------+----------------------------------------------------+
| minion001        | None                       | Remove and roll-out minion001                      |
+------------------+----------------------------+----------------------------------------------------+
| minion002        | None                       | Remove and roll-out minion002                      |
+------------------+----------------------------+----------------------------------------------------+
| minion003        | None                       | Remove and roll-out minion003                      |
+------------------+----------------------------+----------------------------------------------------+
| minion004        | None                       | Remove and roll-out minion004                      |
+------------------+----------------------------+----------------------------------------------------+
| puppetca001      | None                       | Remove and roll-out puppetca001                    |
+------------------+----------------------------+----------------------------------------------------+
| puppetca001_bare | None                       | Remove and roll-out puppetca001, using a bare      |
|                  |                            | overlay                                            |
+------------------+----------------------------+----------------------------------------------------+
| lordship         | None                       | Remove and roll-out minion001..004                 |
+------------------+----------------------------+----------------------------------------------------+
| overlordship     | None                       | Remove and roll-out minion005..008                 |
+------------------+----------------------------+----------------------------------------------------+
| remove_minions   | None                       | Remove all minions                                 |
+------------------+----------------------------+----------------------------------------------------+
