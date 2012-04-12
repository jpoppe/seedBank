=====================
Troubleshooting guide
=====================

Introduction
============

This section is to help you with troubleshooting seedBank usage, seedBank is rock solid but there are many requirements which needs to be fullfilled for successfull usage.

Logging
=======

seedBank provides lots of information by default.

seedBank logs default to /var/log/seedbank.log with the INFO level, you can change this to the DEBUG level by editing the logging configuration file.

.. code-block:: none

    vi /etc/seedbank/logging.conf

If somethings goes wrong during the installation the Debian installer provides several options for debugging. You could switch to the different consoles by using the ALT and arrow keys, or by using the ALT key and the number of the specific console.

* ALT+1 The default console
* ALT+2 Terminal
* ALT+3 Terminal
* ALT+4 Syslog file tailed contiously

Test the daemon
===============

The daemon could be tested by simulating the requests, in this example 'C0A80014' is used for the pxelinux.cfg name which is hexidecimal for '192.168.0.20'. You will need to adjust this to the name of the pxe file generated with the 'seedbank pxe' command.

Test the preseed file

.. code-block:: none

    wget "http://localhost:7467/seed/C0A80014" -q -O -

Test the Puppet manifests

.. code-block:: none

    wget "http://localhost:7467/manifests.tgz"

Test the start installation log message

.. code-block:: none

    wget "http://localhost:7467/pimp/C0A80014" -q -O -

Test the file overlay archive

.. code-block:: none

    wget "http://localhost:7467/overlay.tgz/C0A80014" -O overlay.tgz

Test the disable command, be sure to move the 'C0A80014.disabled' file back to 'C0A80014' for further testing

.. code-block:: none

    wget "http://localhost:7467/disable/C0A80014" -q -O

Write a status file

.. code-block:: none

    wget "http://localhost:7467/status/C0A80014&state=done" -q -O
