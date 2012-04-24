==================
seedBank Changelog
==================

v2.0.0 04/??/2012 (Jasper Poppe)
================================

seedbank general

* almost everything has been rewritten
* removed recipes and added those to seeds since they are actually seeds, use -a/--additional instead of -r/--recipe to specify "disk recipes"
* replaced --custom option with variables option for overriding seed and pxe variables
* switched to one binary
* seedbank -> seedbank pxe
* seedbank_setup -> seedbank manage
* seedbank_daemon -> seedbank daemon
* seedbank list -> for listing resources
* added support for creating unattended ISOs
* seedbank iso
* improved error handling
* improved and more verbose logging
* more verbose help
* removed wget dependency
* switched from optparse to argparse
* improved documentation
* added Mac OS X compatibility for creating ISOs

seedbank daemon

* replaced the default Python webserver with the Bottle Framework (embedded)
* added more pxe variables
* all variables except the 'address' variable are now passed via pxe variables
* added remote calls for enabling hosts for netbooot
* deprecated the file server functionality

seedbank list

* merged configured and available releases into one list and use an asterisk to mark releases/ISOs which are available on the system

configuration/examples

* swiched varible placeholder in seed files from '*' to '$' format for the sake of sanity
* switch configuration format from native Python to YAML
* simplified configuration
* splitted configuration into 2 files (settings.yaml and system.yaml)
* added external logging configuration (logging.conf)
* more variables can be used in the configuration 
* all settings can be overridden with a config overrride file (except for the settings section)
* removed support for Ubuntu Lucid Lynx (still can be added manually)
* added support for Ubuntu Precise Pangolin

And much more ;)

v1.1.0 02/09/2012 (Jasper Poppe)
================================

seedbank.py

* Added '-a', '--seed-additional' option, append additional seed files to the default seed file
* Added '-v', '--variables'option: specify additional pxe variables which could be used by templates in overlays
* Some minor changes

seedbank_daemon.py

* Added status request which will write a file when requested
* Added more default variables to the PXE templates
* Some minor changes

settings.py

* Added status path, default: /var/lib/seedbank/status
* added repository_0 and repository_0_key preseed variables for use with the repository.seed example
* Some minor changes

configuration/examples

* Added an Ubuntu Oneiric seed file
* Remove the Ubuntu Natty seed file (Natty itself is still supported)
* Moved the infrastructure anywhere scripts to a separate Git repository
* Added seedbank_seeds, seedbank_domainname, seedbank_fqdn, seedbank_seed_host, seedbank_seed_port, seedbank_address variables to the pxe templates
* Some minor changes

v1.0.1 09/25/2011 (Jasper Poppe)
================================

* Some minor changes

v1.0.0 09/22/2011 (Jasper Poppe)
================================

* Initial release
