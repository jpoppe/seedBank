===============
MAC OS X (Beta)
===============

Introduction
============

Only ISO support has been tested on Mac OS X Lion.

NOTE: This document contains errors and is incomplete, feel free to improve ;)

Install Prerequisites
=====================

Install Git

.. code-block:: none

    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"
    brew update
    brew install git

Install the pyyaml package

.. code-block:: none

    sudo easy_install-2.7 pyyaml

Install cpio, gnutar and cdrtools via precompiled packages

.. code-block:: none

    cd /tmp
    curl -L -O http://infrastructureanywhere.com/downloads/osx/cdrtools-3.00.zip
    curl -L -O http://infrastructureanywhere.com/downloads/osx/cpio-2.11.zip
    curl -L -O http://infrastructureanywhere.com/downloads/osx/gnutar-1.26.zip
    unzip cdrtools-3.00.zip
    unzip cpio-2.11.zip
    unzip gnutar-1.26.zip
    sudo installer -pkg cdrtools-3.00.pkg -target /
    sudo installer -pkg cpio-2.11.pkg -target /
    sudo installer -pkg gnutar-1.26.pkg -target /

Clone the seedBank git repository and install seedBank

.. code-block:: none

    git clone https://github.com/jpoppe/seedBank.git
    cd seedBank
    sudo ./setup.py install

Install the additional tools vi MacPorts and build OS X packages
================================================================

Install MacPorts

.. code-block:: none

    curl -O https://distfiles.macports.org/MacPorts/MacPorts-2.0.4-10.7-Lion.dmg
    hdiutil mount MacPorts-2.0.4-10.7-Lion.dmg
    sudo installer -pkg /Volumes/MacPorts-2.0.4/MacPorts-2.0.4.pkg -target /
    hdiutil unmount /Volumes/MacPorts-2.0.4

Install cpio, gnutar and cdrtools via macports (will require xcode)

.. code-block:: none

    sudo port selfupdate
    sudo port install smake
    sudo port install cpio gnutar cdrtools

Build and zip OS X packages

.. code-block:: none

    port pkg cpio gnutar cdrtools

    cd ~/.macports/opt/local/var/macports/build/_opt_local_var_macports_sources_rsync.macports.org_release_tarballs_ports_archivers_cpio/cpio/work
    zip -r ~/cpio-2.11.zip cpio-2.11.pkg
    cd ~/.macports/opt/local/var/macports/build/_opt_local_var_macports_sources_rsync.macports.org_release_tarballs_ports_sysutils_cdrtools/cdrtools/work
    zip -r ~/cdrtools-3.00.zip cdrtools-3.00.pkg
    cd ~/.macports/opt/local/var/macports/build/_opt_local_var_macports_sources_rsync.macports.org_release_tarballs_ports_archivers_gnutar/gnutar/work
    zip -r ~/gnutar-1.26.zip gnutar-1.26.pkg

IA Related
==========

Install VirtualBox on Mac OS X

.. code-block:: none

    curl -L -O http://download.virtualbox.org/virtualbox/4.1.8/VirtualBox-4.1.8-75467-OSX.dmg
    hdiutil mount VirtualBox-4.1.8-75467-OSX.dmg
    sudo installer -pkg /Volumes/VirtualBox/VirtualBox.mpkg -target /
    hdiutil unmount /Volumes/VirtualBox
