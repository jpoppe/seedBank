===============================
Creating a Debian/Ubuntu mirror
===============================

reprepro
========

This guide is written for reprepro 4.2.0+. Reprepro is a nice tool to create Debian/Ubuntu mirrors and your own repositories.

As soon as you understand how the tool works it's pretty easy to use.

Installation
------------

Install reprepro on Debian Squeeze

.. code-block:: none

    sudo apt-get install reprepro

GPG Configuration
-----------------

All packages repositories should be signed with your GPG key. To make this as painless as possible use *gpg-agent*.

Install the GNU GPG agent

.. code-block:: none

    sudo apt-get install gnupg-agent

List available GPG keys

.. code-block:: none

    gpg --list-keys

Generate a new GPG key if there is no key availble

.. code-block:: none

    gpg --gen-key

Add the following to *~/.profile* so gpg-agent will be invoked automatically when it is not running

.. code-block:: none

    vi ~/.profile

.. literalinclude:: configs/gnugpg/.profile

Add the following line to your *.bash_profile*

.. code-block:: none

    vi ~/.bash_profile

.. literalinclude:: configs/gnugpg/.bash_profile

Export the gpg key

.. code-block:: none

    gpg --list-keys
    gpg --export -a 6A9E1B52 > key.pub

Add the gpg key to the apt keyring

.. code-block:: none

    sudo apt-key add key.pub

Gather various GPG keys
-----------------------

Get the GPG key for the Debian repository

.. code-block:: none

    cd /tmp
    wget http://ftp.us.debian.org/debian/dists/squeeze/Release
    wget http://ftp.us.debian.org/debian/dists/squeeze/Release.gpg
    gpg Release.gpg # enter: 'Release' as name of data file
    gpg --keyserver subkeys.pgp.net --search-keys "55BE302B" # Enter '1'
    rm Release.gpg Release

Get the GPG key for the Ubuntu repository

.. code-block:: none

    cd /tmp
    wget http://mirrors.kernel.org/ubuntu/dists/natty/Release.gpg
    wget http://mirrors.kernel.org/ubuntu/dists/natty/Release
    gpg Release.gpg # enter: 'Release' as name of data file
    gpg --keyserver subkeys.pgp.net --search-keys 437D05B5 # Enter '1'
    gpg --keyserver subkeys.pgp.net --search-keys 55BE302B # Enter '1'
    rm Release.gpg Release

Run the following command to get the last 16 hex digits of the fingerprint

.. code-block:: none

    gpg --with-colons --list-key
  
.. code-block:: none

    pub:-:4096:1:9AA38DCD55BE302B:2009-01-27:2012-12-31::-:Debian Archive Automatic Signing Key (5.0/lenny) <ftpmaster@debian.org>::scSC:
    pub:-:4096:1:9AA38DCD55BE302B:2009-01-27:2012-12-31::-:Debian Archive Automatic Signing Key (5.0/lenny) <ftpmaster@debian.org>::scSC:

In this case *9AA38DCD55BE302B* is the value to use for the reprepro *VerifyRelease* option in the conf/updates file(s).

Import the key to the GPG keyring and add it to the apt keyring

.. code-block:: none

    gpg --keyserver subkeys.pgp.net --recv AED4B06F473041FA
    gpg --export --armor AED4B06F473041FA | apt-key add -

Partial mirrors
---------------

It is possible to create partially mirrors with reprepro.

The trick is the *FilterFormula* parameter in the *conf/updates* file.

Example

.. code-block:: none

    FilterFormula: Priority (==required)

Create a Debian Squeeze mirror
------------------------------

Create the mirror directory including a conf directory, all mirror data will be stored here, be sure there is enough disk space available since mirrors take quite some disk space.

.. code-block:: none

    mkdir -p /opt/repositories/debian/mirror/conf

Create the "conf/distributions" configuration file

.. code-block:: none

    vi /opt/repositories/debian/mirror/conf/distributions

.. literalinclude:: configs/reprepro/debian/distributions

Create the "conf/updates" configuration file

.. code-block:: none

    vi /opt/repositories/debian/mirror/conf/updates

.. literalinclude:: configs/reprepro/debian/updates

Sync/Update the mirror

.. code-block:: none

    cd /opt/repositories/debian/mirror
    reprepro -V update

Create a Debian Squeeze proposed updates mirror
-----------------------------------------------

Create the mirror directory including a conf directory, all mirror data will be stored here, be sure there is enough disk space available since mirrors take quite some disk space.

.. code-block:: none

    mkdir -p /opt/repositories/debian/proposed-updates/conf

Create the "conf/distributions" configuration file

.. code-block:: none

    vi /opt/repositories/debian/proposed-updates/conf/distributions

.. literalinclude:: configs/reprepro/debian-proposed/distributions

Create the "conf/updates" configuration file

.. code-block:: none

    vi /opt/repositories/debian/proposed-updates/conf/updates

.. literalinclude:: configs/reprepro/debian-proposed/updates

Sync/Update the mirror

.. code-block:: none

    cd /opt/repositories/debian/proposed-updates
    reprepro -V update

Create a Debian Squeeze backports mirror
----------------------------------------

Create the mirror directory including a conf directory, all mirror data will be stored here, be sure there is enough disk space available since mirrors take quite some disk space.

.. code-block:: none

    mkdir -p /opt/repositories/debian/backports/conf

Create the "conf/distributions" configuration file

.. code-block:: none

    vi /opt/repositories/debian/backports/conf/distributions

.. literalinclude:: configs/reprepro/debian-backports/distributions

Create the "conf/updates" configuration file

.. code-block:: none

    vi /opt/repositories/debian/backports/conf/updates

.. literalinclude:: configs/reprepro/debian-backports/updates

Sync/Update the mirror

.. code-block:: none

    cd /opt/repositories/debian/backports
    reprepro -V update

Create a Ubuntu Natty mirror
-------------------------------

Create a directory including a conf directory which will contain the mirror(s)

.. code-block:: none

    mkdir -p /opt/repositories/ubuntu/mirror/conf

Create the "conf/distributions" configuration file

.. code-block:: none

    vi /opt/repositories/ubuntu/mirror/conf/distributions

.. literalinclude:: configs/reprepro/ubuntu/distributions

Create the "conf/updates" configuration file

.. code-block:: none

    vi /opt/repositories/ubuntu/mirror/conf/updates

.. literalinclude:: configs/reprepro/ubuntu/updates

Sync/Update the mirror

.. code-block:: none

    cd /opt/repositories/ubuntu/mirror
    reprepro -V update

Create a custom repository
--------------------------

Create the directory structure

.. code-block:: none

    sudo mkdir -p /opt/repositories/debian/custom/conf
  
Create the configuration file

.. code-block:: none

    sudo vi /opt/repositories/debian/custom/conf/distributions

.. code-block:: none

    Origin: custom
    Label: Custom Debian Repository
    Codename: squeeze
    Architectures: i386 amd64 source
    Components: main
    Description: This repository contains custom Debian packages
    SignWith: your public gpgkey # (use gpg --list-keys to get the key)

Create the options file

.. code-block:: none

    vi /opt/repositories/debian/custom/conf/options

.. code-block:: none

    basedir /opt/repositories/debian/custom
  
Add a package to the repository

.. code-block:: none

    cd /opt/repositories/debian/custom
    reprepro includedeb custom ~/seedbank_0.8.0_all.deb

Various reprepro commands
-------------------------

List all available packages for Debian Squeeze in the custom repository

.. code-block:: none

    reprepro -b /opt/repositories/debian/custom list squeeze
    cd /opt/repositories/debian/custom
    reprepro list squeeze
  
Add a Debian package to the custom repository

.. code-block:: none

    reprepro -Vb /opt/repositories/debian/custom includedeb squeeze ~/seedbank_0.8.0_all.deb

Remove the *seedbank* package from the custom repository

.. code-block:: none

    reprepro -Vb /opt/repositories/debian/custom remove squeeze seedbank

nginx
-----

The repository or repositories need to be accessible, one way to do is is via the very fast an lighweight web server Nginx.

Install Nginx

.. code-block:: none

    sudo apt-get install nginx

Make sure you have a CNAME configured in DNS which points to the *server_name* configuration directive.

Create a virtual host

.. code-block:: none

    sudo vi /etc/nginx/sites-available/packages

.. code-block:: none

    server {

        listen      80;
        server_name packages.seedbank.local;
        autoindex   on;

        access_log /var/log/nginx/packages-access.log;
        error_log  /var/log/nginx/packages-error.log;

        location / {
            root /opt/repositories;
            index index.html;
        }
    
    }

Enable the virtual host

.. code-block:: none

    sudo ln -s /etc/nginx/sites-available/packages /etc/nginx/sites-enabled/
    sudo /etc/init.d/nginx restart

Resources
---------

Official
 * http://mirrorer.alioth.debian.org/
 * http://nginx.org/ 
 * http://www.gnupg.org/

Lists with official Mirrors
  * http://www.debian.org/mirror/list
  * http://www.ubuntu.com/getubuntu/downloadmirrors

Reprepro
 * http://davehall.com.au/blog/dave/2010/02/06/howto-setup-private-package-repository-reprepro-nginx
 * http://www.jejik.com/articles/2006/09/setting_up_and_managing_an_apt_repository_with_reprepro/
 * http://www.debianx.org/repo.html
 * http://www.porcheron.info/setup-your-debianubuntu-repository-with-reprepro/
 * http://www.lostwebsite.net/2008/10/partial-debian-mirrors/

GnuPG
 * http://www.gentoo.org/doc/en/gnupg-user.xml
 * http://irtfweb.ifa.hawaii.edu/~lockhart/gpg/gpg-cs.htm 

Other mirror tools
==================

There is a handful of other mirror tools available, some to create full mirrors, some to create proxying mirrors.

If disk space/bandwith is an issue take a look to "apt-cacher", a really nice easy to setup proxy based mirror.
Unfortunately the last time I've checked it didn't like mixing distributions like Debian and Ubuntu together.

More information about some of the available tools
 * http://help.ubuntu.com/community/Apt-Cacher-Server
 * http://packages.debian.org/squeeze/apt-cacher
 * http://packages.qa.debian.org/a/apt-cacher.html
 * http://apt-proxy.sourceforge.net/
 * http://apt-mirror.sourceforge.net/
