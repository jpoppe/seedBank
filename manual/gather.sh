#!/bin/bash

#for component in prepare net iso daemon; do
#	sudo seedbank --help ${component} > core/help/seedbank.py
#done

#rm ./seedbank.rst
sphinx-apidoc -f -T -o . ~/git/seedbank/seedbank/
rm help/seedbank
#seedbank 2>1 > help/seedbank

seedbank --help > help/seedbank
#echo "" >> help/seedbank
seedbank list --help > help/seedbank_list
#echo "" >> help/seedbank_list
seedbank net --help > help/seedbank_net
#echo "" >> help/seedbank_net
seedbank iso --help > help/seedbank_iso
#echo "" >> help/seedbank_iso
seedbank manage --help > help/seedbank_manage
#echo "" >> help/seedbank_manage
seedbank daemon --help > help/seedbank_daemon
#echo "" >> help/seedbank_daemon
