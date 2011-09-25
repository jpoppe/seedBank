# Copyright 2011, Jasper Poppe <jpoppe@ebay.com>, Lex van Roon
# <lvanroon@ebay.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#
# add_domain('a.c.m.e', 'NATIVE')
# add_domain('20.168.192.in-addr.arpa', 'NATIVE')
# add_record('1', 'a.c.m.e', 'ns1.overlord001.a.c.m.e jpoppe@ebay.com 2011050900 86400 7200 3600000 86400', 'SOA', '86400', 'NULL')
# add_record('1', 'a.c.m.e', 'ns1.overlord001.a.c.m.e', 'NS', '86400', 'NULL')
# add_record('1', 'a.c.m.e', 'ns2.overlord002.a.c.m.e', 'NS', '86400', 'NULL')
# add_record('1', 'a.c.m.e', 'mail.overlord001.a.c.m.e', 'MX', '120', '25')
# add_record('1', 'a.c.m.e', 'mail.overlord002.a.c.m.e', 'MX', '120', '25')
# add_record('1', 'ns1.overlord001.a.c.m.e', '192.168.20.1', 'A', '120', 'NULL')
# add_record('1', 'ns2.overlord002.a.c.m.e', '192.168.20.2', 'A', '120', 'NULL')
# add_record('1', 'overlord001.a.c.m.e', 'mail.overlord001.a.c.m.e', 'MX', '120', '10')
# add_record('1', 'overlord002.a.c.m.e', 'mail.overlord002.a.c.m.e', 'MX', '120', '20')
# add_record('1', 'overlord001.a.c.m.e', '192.168.20.1', 'A', '120', 'NULL')
# add_record('1', 'overlord002.a.c.m.e', '192.168.20.2', 'A', '120', 'NULL')
# add_record('2', '1.20.168.192.in-addr.arpa', 'overlord001.a.c.m.e', 'PTR', 'NULL', 'NULL')
# add_record('2', '2.20.168.192.in-addr.arpa', 'overlord002.a.c.m.e', 'PTR', 'NULL', 'NULL')
#
from __future__ import with_statement
from fabric.api import run, settings, hosts, env, hide

def _reverse_ip(ipaddress):
    ipreverse = ipaddress.split('.')
    ipreverse.reverse()
    return '.'.join(ipreverse)

def add_domain(name, dns_type):
    for overlord in env['overlord']:
        with settings(host_string=overlord, user='root'):
            run('mysql --defaults-extra-file=/root/.my.cnf -e "INSERT INTO domains (name, type) VALUES (\'%s\', \'%s\')" pdns' % (name, dns_type))

def add_record(domain_id, name, content, dns_type, ttl, prio):
    for overlord in env['overlord']:
        with settings(host_string=overlord, user='root'):
            run('mysql --defaults-extra-file=/root/.my.cnf -e\
                "INSERT INTO records (domain_id, name, content, type, ttl ,prio)\
                VALUES (%s, \'%s\', \'%s\', \'%s\', %s, %s)" pdns' % 
                (domain_id, name, content, dns_type, ttl, prio))

def remove_record(name):
    for overlord in env['overlord']:
        with settings(host_string=overlord, user='root'):
            run('mysql --defaults-extra-file=/root/.my.cnf -e "DELETE FROM records WHERE name = \'%s\'" pdns' % name)

def add_host(name, macaddress, ipaddress):
    for overlord in env['overlord']:
        with settings(host_string=overlord, user='root'):
            add_record('1', '%s.%s' % (name, env['dns_domain']), ipaddress, 'A', '120', 'NULL')
            add_record('2', '%s.in-addr.arpa' % _reverse_ip(ipaddress), '%s.%s' % (name, env['dns_domain']), 'PTR', 'NULL', 'NULL')
            run('echo "dhcp-host=%s,%s,%s,infinite" > /etc/dnsmasq.d/%s' % (macaddress, name, ipaddress, name))
            run('/etc/init.d/dnsmasq restart')

def remove_host(name, ipaddress):
    for overlord in env['overlord']:
        with settings(host_string=overlord, user='root', warn_only=True):
            remove_record('%s.a.c.m.e' % name)
            remove_record('%s.in-addr.arpa' % _reverse_ip(ipaddress))
            run('rm /etc/dnsmasq.d/%s' % name)
            run('/etc/init.d/dnsmasq restart')

def update_dns_domain():
    for overlord in env['overlord']:
        with settings(hide('stdout', 'stderr'), host_string=overlord, user='root'):
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE domains SET name=\'%s\' WHERE id=1" pdns' % env['dns_domain'])
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'%s\', content=\'ns1.%s jpoppe@ebay.com 2011050900 86400 7200 3600000 86400\' WHERE domain_id = 1 AND name=\'a.c.m.e\' AND type=\'SOA\'" pdns' % (env['dns_domain'], env['dns_domain']))
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'%s\', content=\'ns1.overlord001.%s\' WHERE domain_id=1 AND name=\'a.c.m.e\' AND type=\'NS\' AND content=\'ns1.overlord001.a.c.m.e\'" pdns' % (env['dns_domain'], env['dns_domain']))
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'%s\', content=\'ns2.overlord002.%s\' WHERE domain_id=1 AND name=\'a.c.m.e\' AND type=\'NS\' AND content=\'ns2.overlord002.a.c.m.e\'" pdns' % (env['dns_domain'], env['dns_domain']))
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'ns1.overlord001.%s\' WHERE domain_id=1 AND name=\'ns1.overlord001.a.c.m.e\'" pdns' % env['dns_domain'])
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'ns2.overlord002.%s\' WHERE domain_id=1 AND name=\'ns2.overlord002.a.c.m.e\'" pdns' % env['dns_domain'])
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'%s\', content=\'mail.overlord001.%s\' WHERE domain_id=1 AND content=\'mail.overlord001.a.c.m.e\'" pdns' % (env['dns_domain'], env['dns_domain']))
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'%s\', content=\'mail.overlord002.%s\' WHERE domain_id=1 AND content=\'mail.overlord002.a.c.m.e\'" pdns' % (env['dns_domain'], env['dns_domain']))
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'overlord001.%s\' WHERE domain_id=1 AND name=\'overlord001.a.c.m.e\'" pdns' % env['dns_domain'])
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'overlord002.%s\' WHERE domain_id=1 AND name=\'overlord002.a.c.m.e\'" pdns' % env['dns_domain'])
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'overlord001.%s\' WHERE domain_id=2 AND name=\'overlord001.a.c.m.e\'" pdns' % env['dns_domain'])
            run('mysql --defaults-extra-file=/root/.my.cnf -e "UPDATE records SET name=\'overlord002.%s\' WHERE domain_id=2 AND name=\'overlord002.a.c.m.e\'" pdns' % env['dns_domain'])
            run('sed -ie \'s,ca = false,ca = true,g\' /etc/puppet/puppetmaster.conf')
            run('rm -f /etc/puppet/puppetmaster.confe')
            run('/etc/init.d/puppetmaster restart')
            run('/etc/init.d/nginx restart')
        with settings(host_string=overlord):
            run('puppetd -t || true')

def uname():
    for overlord in env['overlord']:
        with settings(host_string=overlord, user='root'):
            run('uname -a')

if __name__ == 'powerdns':
    from fabric.api import env, hosts

    #name = 'minion001'
    #ip_address = '192.168.20.1'
    #remove_host(name, ip_address)
    #powerdns.add_host(name, env['mac'], ip_address)
