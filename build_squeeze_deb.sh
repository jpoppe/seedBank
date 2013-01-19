###############################################################################
# reference: http://wiki.debian.org/Python/Packaging
###############################################################################

#sudo apt-get install pbuilder debian-archive-keyring python-stdeb python-distutils-extra python-setuptools git
#mkdir ~/git
#git clone https://github.com/jpoppe/seedBank.git ~/git/seedbank

rm -rf /tmp/seedbank_deb
mkdir /tmp/seedbank_deb
cp -r ~/git/seedbank /tmp/seedbank_deb
rm -rf /tmp/seedbank_deb/seedbank/.git
rm -rf /tmp/seedbank_deb/seedbank/debian
cd /tmp/seedbank_deb/seedbank
python setup.py sdist
cp dist/seedbank-2.0.0rc7.tar.gz /tmp/seedbank_deb
cd /tmp/seedbank_deb
py2dsc -m "Jasper Poppe <jgpoppe@gmail.com>" seedbank-2.0.0rc7.tar.gz
cd deb_dist/seedbank-2.0.0rc7
cp ~/git/seedbank/deb/init.d debian
cp ~/git/seedbank/deb/changelog debian
echo  "/usr/share/seedbank/seedbank/seedbank /usr/bin/seedbank" > debian/links
echo  "README.rst" > debian/docs
sed -i "s/python-seedbank/seedbank/" debian/control
sed -i "s/python-all/python/g" debian/control
sed -i "7 iX-Python-Version: >= 2.6" debian/control
sed -i "11 iHomepage: http://www.infrastructureanywhere.com" debian/control
sed -i "12 iSuggests: dhcp3-server, tftpd-hpa, bind9, dnsmasq" debian/control
sed -i "/^Depends: / s/$/ python-yaml, python-argparse, python-lxml, bsdtar, genisoimage/" debian/control
sed -i "s/\${python:Depends}/python (>= 2.6),/" debian/control
sed -i "s/ --buildsystem=python_distutils//" debian/rules
sed -i "$ i\\
override_dh_auto_install:\\
\tpython setup.py install --root=debian/seedbank --install-layout=deb --install-lib=/usr/share/seedbank --install-scripts=/usr/share/seedbank\\
override_dh_auto_build:" debian/rules
debuild
sudo pbuilder build ../*.dsc

#scp /var/cache/pbuilder/result/seedbank_2.0.0rc7-1_all.deb root@overlord001.xxx.ebuddy.com:
#ssh overlord001.xxx.ebuddy.com "dpkg -i seedbank_2.0.0rc7-1_all.deb; apt-get -f install"
