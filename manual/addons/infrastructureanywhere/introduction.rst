============
Introduction
============

--------------------------------
What is Infrastructure Anywhere?
--------------------------------
Infrastructure Anywhere is a command-line based deployment tool, written in fabric. It's written in such a way that it can be easily extended to support multiple virtualisation technologies. It has been written with Puppet in mind, so it's possible to bootstrap puppet automatically after finishing with an installation. Within these documents, IA is the abbreviation of Infrastructure Anywhere.

-----------
Terminology
-----------
TODO: add terminology

-----------------
What is supported
-----------------
Currently, only libvirt/kvm is properly supported. Work is underway to support VirtualBox, VMWare ESX and physical platforms, but that is incomplete as of the writing of these documents. With libvirt/kvm, it's possible to use it as a multi-user setup.

------------
How it works
------------
IA acts as a wrapper around the chosen virtualisation platform. In the current design it uses a custom iso to bootstrap a puppetmaster. Further hosts are bootstrapped off this puppetmaster using seedBank. Depending on your Puppet code it allows you to bootstrap a separate CA server. A full list of available commands and their descriptions can be found in :doc:`usage`
