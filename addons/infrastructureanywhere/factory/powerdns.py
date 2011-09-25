#!/usr/bin/env python

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

""" powerdns.py (c) 2011 - Lex van Roon <lvanroon@ebay.com>

    A module to manage powerdns
"""

__author__ = 'Lex van Roon <lvanroon@ebay.com>'
__copyright__ = 'Copyright (c) 2011 Lex van Roon'
__credits__ = ''
__license__ = 'copyright'
__version__ = '0.2'
__maintainer__ = 'Lex van Roon'
__email__ = 'lvanroon@ebay.com'
__status__ = 'in development'

import MySQLdb

class PowerDNS:
    """ A class to manage a PowerDNS server through MySQL
    """
    _debug_sql = False
    _defaults = {
        'primary_dns': 'ns1.overlord001.a.c.m.e',
        'hostmaster': 'lvanroon@ebay.com',
        'ttl': 86400,
        'refresh': 7200,
        'expire': 3600000,
        'minimum': 86400,
    }
    _domain_types = ['MASTER', 'SLAVE', 'NATIVE']
    _record_types = ['A', 'AAAA', 'CNAME', 'HINFO', 'MX', 'NAPTR', 'NS',
                     'PTR', 'SOA', 'SPF', 'SRV', 'SSHFP', 'TXT', 'RP']
    db_connection = None
    cursor = None

    def __init__(self, host, username, password, database):
        """ Initialize this class, set variables to be used later on

            Requires:
            * host     -> string, host to connect to
            * username -> string, username to use
            * password -> string, password to use
            * database -> string, database to connect to

            Returns:
            * None
        """
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    def connect(self):
        """ Connect to the database and create a cursor object

            Requires:
            * None

            Returns:
            * None
        """
        self.db_connection = MySQLdb.connect(host=self.host,
                                             user=self.username,
                                             passwd=self.password)
        self.db_connection.select_db(self.database)
        self.db_connection.autocommit(True)
        self.cursor = self.db_connection.cursor()

    @classmethod
    def _reverse_zone(cls, ip_address):
        """ Get the name of the reverse zone of a given ip address
            Note that this works on /24 boundaries only

            Requires:
            * ip_address -> string, ip address to use

            *Returns:
            * string, name of the in-addr.arpa zone
        """
        tmp = ip_address.split(".")[:3]
        tmp.reverse()
        return "%s.in-addr.arpa" % (".".join(tmp))

    def _query(self, sql, args=None):
        """ Run a sql query and print it, if enabled

            Requires:
            * sql -> string, SQL query to perform

            Returns:
            * None
        """
        if args:
            if not isinstance(args, tuple):
                args = (args)
            if self._debug_sql:
                print sql % self.db_connection.literal(args)
            self.cursor.execute(sql, args)
        else:
            if self._debug_sql:
                print sql
            self.cursor.execute(sql)

    def _validate_arg(self, arg, value):
        """ Validate arguments that need special handling

            Required:
            * arg   -> argument to work on
            * value -> value for this argument

            Returns:
            * str -> message containing error message
            * None -> when there are no errors
        """
        if arg == 'domain_type' and not value in self._domain_types:
            return 'domain_type needs to be one of %s' % \
                    ', '.join(self._domain_types)
        elif arg == 'record_type' and not value in self._record_types:
            return 'record_type needs to be one of %s' % \
                    ', '.join(self._record_types)
        elif arg == 'name_servers' and not isinstance(value, dict):
            return 'name_servers needs to be a dictionary'
        elif arg == 'mail_exchangers' and not isinstance(value, dict):
            return 'mail_exchangers needs to be a dictionary'

    def _parse_kwargs(self, args, used, required):
        """ Validate arguments and set defaults if needed

            Requires:
            * args     -> dict, kwargs for a function
            * used     -> list, options that are used
            * required -> list, options that are required

            Returns:
            * dict -> Validated kwargs containing default values if needed
        """
        for opt in used:
            if opt in args:
                errmsg = self._validate_arg(opt, args[opt])
                if errmsg:
                    print errmsg
                    return
            else:
                if opt in required:
                    print('function needs %s' % opt)
                    return
                else:
                    if opt in self._defaults:
                        args[opt] = self._defaults[opt]
                    else:
                        args[opt] = None
        return args

    def has_domain(self, name):
        """ Check if a domain exists.

            Requires:
            * name -> string, name of the domain to check

            Returns:
            * long, the domain_id if the domain is found
            * None, if nothing is found
        """
        self._query('SELECT id FROM domains WHERE name = %s', name)
        data = self.cursor.fetchone()
        if data:
            return data[0]

    def has_reverse(self, ip_address):
        """ Check if a reverse domain exists for a given ip address

            Requires:
            * ip_address -> string, ip address to use for in-addr.arpa zone

            Returns:
            * long, the domain_id if the domain is found
            * None, if the domain is not found
        """
        return self.has_domain(self._reverse_zone(ip_address))

    def list_domains(self):
        """ Print a list of domains

            Requires:
            * None

            Returns:
            * None
        """
        spacer = " " * 34
        print ('domain%stype' % spacer)
        print ('-' * 47)
        self._query('SELECT * FROM domains ORDER BY name,type')
        for row in self.cursor.fetchall():
            print ('%s%s') % (row[1].ljust(40), row[4])
        print ('')

    def get_domain_id(self, name):
        """ Retrieve the ID of a given domain

            Requires:
            * name -> string, name of the domain

            Returns:
            * long, domain_id of the domain
            * None, if the domain is not found
        """
        self._query('SELECT id FROM domains WHERE name = %s', name)
        data = self.cursor.fetchone()
        if data:
            return data[0]

    def get_domain_name_by_id(self, domain_id):
        """ Get the name of a given domain_id

            Requires:
            * domain_id -> long, domain id of the domain

            Returns:
            * string, name of the domain
        """
        self._query('SELECT name FROM domains WHERE id = %s', domain_id)
        data = self.cursor.fetchone()
        if data:
            return data[0]

    def add_domain(self, name, domain_type='MASTER', master='127.0.0.1'):
        """ Add a domain to the database

            Requires:
            * name        -> string, name of the domain
            * domain_type -> string, MASTER, SLAVE or NATIVE. Defaults to
                             'MASTER'
            * master      -> string, ip address of the zone master. Defaults
                             to '127.0.0.1'

            Returns:
            * None
        """
        if self.has_domain(name):
            print ('domain %s already exists' % name)
            return
        if not domain_type in self._domain_types:
            print ('add_domain -> domain_type needs to be one of NATIVE, \
                   MASTER or SLAVE')
            return
        if domain_type == 'SLAVE':
            data = (name, domain_type, master)
            self._query('INSERT INTO domains (name, type, master) VALUES \
                        (%s, %s, %s)', data)
        else:
            data = (name, domain_type)
            self._query('INSERT INTO domains (name, type) VALUES (%s, %s)', \
                        data)

    def remove_domain(self, name):
        """ Remove a domain from the database

            Requires:
            * name -> string, name of the domain to remove

            Returns:
            * None
        """
        if not self.has_domain(name):
            print ('domain %s does not exist' % name)
            return
        self._query('DELETE FROM domains WHERE name = %s', name)

    def has_record(self, domain_id, name, record_type, content=None):
        """ Check if a record exists in the database

            Requires:
            * domain_id -> long, domain_id of the domain to check
            * name      -> string, name of the record
            * record_type -> string, type of the record
            * content     -> string, content of the record. Defaults to None

            Returns:
            * long, the record_id of the record found
            * None, if the record is not found
        """
        if content and record_type != 'PTR':
            data = (domain_id, name, record_type, content)
            self._query('SELECT id FROM records WHERE domain_id = %s AND \
                        name = %s AND type = %s AND content = %s', data)
        else:
            data = (domain_id, name, record_type)
            self._query('SELECT id FROM records WHERE domain_id = %s AND \
                        name = %s AND type = %s', data)
        data = self.cursor.fetchone()
        if data:
            return data[0]

    def get_record_id(self, domain_id, name, record_type, content=None):
        """ Retrieve the ID of a given database record

            Requires:
            * domain_id -> long, domain_id of the domain to check
            * name      -> string, name of the record
            * record_type -> string, type of the record
            * content     -> string, content of the record. Defaults to None

            Returns:
            * long, the record_id of the record found
            * None, if the record is not found
        """
        if content:
            data = (domain_id, name, record_type, content)
            self._query('SELECT id FROM records WHERE domain_id = %s AND \
                        name = %s AND type = %s AND content = %s', data)
        else:
            data = (domain_id, name, record_type)
            self._query('SELECT id FROM records WHERE domain_id = %s AND \
                        name = %s AND type = %s', data)
        data = self.cursor.fetchone()
        if data:
            return data[0]

    def list_records(self, domain_id):
        """ Print all records for a given domain

            Requires:
            * domain_id -> long, domain_id of the domain

            Returns:
            * None
        """
        spacer1 = ' ' * 24
        spacer2 = ' ' * 6
        print ('record%stype%scontent' % (spacer1, spacer2))
        print ('-' * 60)
        self._query('SELECT * FROM records WHERE domain_id = %s ORDER BY \
                    type,name', domain_id)
        for row in self.cursor.fetchall():
            print ('%s%s%s' % (row[2].ljust(30), row[3].ljust(10), row[4]))
        print ('')

    def add_record(self, **kwargs):
        """ Add a record to the database for a given domain

            Requires:
            * domain_id   -> long, domain_id of the domain to add the record to
            * name        -> string, name of the record
            * record_type -> string, type of the record
            * content     -> string, data for this record
            * ttl         -> int, TTL value for this record. Defaults to 86400

            Returns:
            * None
        """
        opts = ['domain_id', 'name', 'record_type', 'content', 'ttl']
        for opt in opts:
            if opt in kwargs:
                if opt == 'record_type' and \
                        not kwargs['record_type'] in self._record_types:
                    print('%s is a invalid record_type' % 
                          kwargs['record_type'])
                    return
            else:
                if opt in ['domain_id', 'name', 'record_type']:
                    print('add_record() needs %s' % opt)
                    return
                elif opt == 'content':
                    kwargs[opt] = None
                else:
                    kwargs[opt] = self._defaults[opt]

        if self.has_record(kwargs['domain_id'], kwargs['name'],
                           kwargs['record_type'], kwargs['content']):
            print ('record %s %s already exists' % (kwargs['name'],
                                                    kwargs['record_type']))
            return
        data = (kwargs['domain_id'], kwargs['name'], kwargs['record_type'],
                kwargs['content'], kwargs['ttl'])
        self._query('INSERT INTO records (domain_id, name, type, content, ttl) \
                    VALUES (%s, %s, %s, %s, %s)', data)

    def remove_record(self, domain_id, name, record_type, content=None):
        """ Remove a record from the database for a given domain

            Requires:
            * domain_id   -> long, domain_id of the domain to remove the
                             record from
            * name        -> string, name of the record
            * record_type -> string, type of the record

            Optional:
            * content     -> string, content of the record. Defaults to None

            Returns:
            * None
        """
        if not self.has_record(domain_id, name, record_type):
            print ('record %s %s does not exist' % (name, record_type))
            return
        if content:
            data = (domain_id, name, record_type, content)
            self._query('DELETE FROM records WHERE domain_id = %s AND \
                    name = %s AND type = %s AND content = %s', data)
        else:
            data = (domain_id, name, record_type)
            self._query('DELETE FROM records WHERE domain_id = %s AND \
                        name = %s AND type = %s', data)

    def update_record(self, **kwargs):
        """ Update a record for a given record id

            Requires:
            * record_id   -> long, record_id of the record
            * name        -> string, name of the record
            * record_type -> string, type of the record
            * content     -> string, content of the record

            Optional:
            * ttl         -> int, TTL for the record. Defaults to 86400

            Returns:
            * None
        """
        opts = ['name', 'record_type', 'content', 'record_id']
        for opt in opts:
            if opt in kwargs:
                if opt == 'record_type' and not kwargs[opt] \
                        in self._record_types:
                    print('%s is not a valid record type' %
                          kwargs['record_type'])
                    return
            else:
                if opt in ['name', 'record_type', 'content']:
                    print('update_record() needs %s' % opt)
                    return
                else:
                    kwargs[opt] = self._defaults[opt]
        data = (kwargs['name'], kwargs['record_type'], kwargs['content'],
                kwargs['ttl'], kwargs['record_id'])
        self._query('UPDATE records SET name = %s, type = %s, content = %s, \
                    ttl = %s WHERE id = %s', data)

    def create_domain(self, **kwargs):
        """ Create a new domain and fill it with default records

            Requires:
            * name         -> string, name of the domain
            * domain_type  -> string, domain type
            * name_servers -> dict, nameservers for this domain

            Optional:
            * mail_exchangers -> dict, mailservers for this domain
            * primary_dns -> string, primary dns server
            * hostmaster  -> string, email address of the hostmaster
            * master      -> string, ip address of the master server
            * ttl         -> int, Time-To-Live value
            * refresh     -> int, Refresh value
            * expire      -> int, Expire value
            * minimum     -> int, Minimum value

            Returns:
            * None
        """
        opts = ['name', 'domain_type', 'name_servers', 'mail_exchangers',
                'primary_dns', 'hostmaster', 'master', 'ttl', 'refresh',
                'expire', 'minimum']
        required = ['name', 'domain_type', 'name_servers']
        kwargs = self._parse_kwargs(kwargs, opts, required)

        self.add_domain(kwargs['name'], kwargs['domain_type'])
        domain_id = self.get_domain_id(kwargs['name'])

        self.add_record(domain_id=domain_id, name=kwargs['name'],
                        record_type='SOA', content='%s %s 1 %s %s %s %s'
                        % (kwargs['primary_dns'], kwargs['hostmaster'],
                        kwargs['ttl'], kwargs['refresh'], kwargs['expire'],
                        kwargs['minimum']))

        if 'name_servers' in kwargs:
            for server_name, server_ip in kwargs['name_servers'].items():
                self.add_record(domain_id=domain_id, name=kwargs['name'],
                                record_type='NS', content=server_name)
                if not 'in-addr.arpa' in kwargs['name']:
                    self.create_host(domain_id=domain_id,
                                     name=server_name,
                                     ip_address=server_ip,
                                     domain_type=kwargs['domain_type'],
                                     name_servers=kwargs['name_servers'],
                                     primary_dns=kwargs['primary_dns'],
                                     hostmaster=kwargs['hostmaster'],
                                     ttl=kwargs['ttl'],
                                     refresh=kwargs['refresh'],
                                     expire=kwargs['expire'],
                                     minimum=kwargs['minimum'])
        if 'mail_exchangers' in kwargs and not 'in-addr.arpa' in kwargs['name']:
            prio = 10
            for server_name, server_ip in kwargs['mail_exchangers'].items():
                self.add_record(domain_id=domain_id, name=kwargs['name'],
                                record_type='MX', content='%s %s' %
                                (prio, server_name))
                self.create_host(domain_id=domain_id,
                                 name=server_name,
                                 ip_address=server_ip,
                                 domain_type=kwargs['domain_type'],
                                 name_servers=kwargs['name_servers'],
                                 primary_dns=kwargs['primary_dns'],
                                 hostmaster=kwargs['hostmaster'],
                                 ttl=kwargs['ttl'],
                                 refresh=kwargs['refresh'],
                                 expire=kwargs['expire'],
                                 minimum=kwargs['minimum'])
                prio += 10

    def create_host(self, **kwargs):
        """ Add a host to the database with a forward + reverse record.
            create the reverse zone if it does not exist

            Required:
            * domain_id  -> long, domain_id for the domain that contains
                           this record
            * name       -> string, name of the record
            * ip_address -> string, ip address for this record

            Optional:
            * name_servers    -> dict, nameservers for this domain
            * mail_exchangers -> dict, mailservers for this domain
            * primary_dns     -> string, primary dns server
            * hostmaster      -> string, email address of the hostmaster
            * master          -> string, ip address of the master server
            * ttl             -> int, Time-To-Live value
            * refresh         -> int, Refresh value
            * expire          -> int, Expire value
            * minimum         -> int, Minimum value

            Returns:
            None
        """
        opts = ['domain_id', 'name', 'ip_address', 'domain_type',
                'name_servers', 'primary_dns', 'hostmaster', 'master',
                'ttl', 'refresh', 'expire', 'minimum']
        required = ['domain_id', 'name', 'ip_address']
        kwargs = self._parse_kwargs(kwargs, opts, required)

        reverse_zone = self._reverse_zone(kwargs['ip_address'])
        if not self.has_domain(reverse_zone):
            required = ['domain_type', 'name_servers', 'primary_dns',
                        'hostmaster']
            for opt in required:
                if not kwargs[opt]:
                    print('create_domain() needs %s' % (opt))
                    return

            self.create_domain(name=reverse_zone,
                               domain_type=kwargs['domain_type'],
                               name_servers=kwargs['name_servers'],
                               mail_exchangers=None,
                               primary_dns=kwargs['primary_dns'],
                               hostmaster=kwargs['hostmaster'],
                               ttl=kwargs['ttl'],
                               refresh=kwargs['refresh'],
                               expire=kwargs['expire'],
                               minimum=kwargs['minimum'])

        reverse_domain_id = self.get_domain_id(reverse_zone)
        host_octet = kwargs['ip_address'].split(".")[3:][0]
        if not self.has_record(kwargs['domain_id'], kwargs['name'], 'A',
                               kwargs['ip_address']):
            self.add_record(domain_id=kwargs['domain_id'], name=kwargs['name'],
                            record_type='A', content=kwargs['ip_address'])
        if not self.has_record(reverse_domain_id, host_octet, 'PTR',
                               kwargs['name']):
            self.add_record(domain_id=reverse_domain_id, name=host_octet,
                            record_type='PTR', content=kwargs['name'])

if __name__ == '__main__':
    NAMESERVERS = {
        'ns1.overlord001.a.c.m.e': '192.168.20.1',
        'ns2.overlord002.a.c.m.e': '192.168.20.2'
    }
    MAILSERVERS = {
        'mail.overlord001.a.c.m.e': '192.168.20.1',
        'mail.overlord002.a.c.m.e': '192.168.20.2'
    }

    PDNS = PowerDNS('192.168.122.2', 'pdns', 'pdns123', 'pdns')
    PDNS.connect()

    if PDNS.has_domain('a.c.m.e'):
        PDNS.remove_domain('a.c.m.e')
    if PDNS.has_domain('20.168.192.in-addr.arpa'):
        PDNS.remove_domain('20.168.192.in-addr.arpa')

    PDNS.create_domain(name='a.c.m.e',
                       domain_type='MASTER',
                       name_servers=NAMESERVERS,
                       mail_exchangers=MAILSERVERS,
                       primary_dns='ns1.overlord001.a.c.m.e',
                       hostmaster='lvanroon@ebay.com')

    FWD_ID = PDNS.get_domain_id('a.c.m.e')
    REV_ID = PDNS.get_domain_id('20.168.192.in-addr.arpa')

    PDNS.create_host(domain_id=FWD_ID, name='overlord001.a.c.m.e',
                     ip_address='192.168.20.1')
    PDNS.create_host(domain_id=FWD_ID, name='overlord002.a.c.m.e',
                     ip_address='192.168.20.2')

    REC_ID = PDNS.get_record_id(REV_ID, '1', 'PTR')
    PDNS.update_record(record_id=REC_ID, name='1', record_type='PTR',
                       content='overlord001.a.c.m.e')

    REC_ID = PDNS.get_record_id(REV_ID, '2', 'PTR')
    PDNS.update_record(record_id=REC_ID, name='2', record_type='PTR',
                       content='overlord002.a.c.m.e')

    PDNS.list_domains()
    PDNS.list_records(FWD_ID)
    PDNS.list_records(REV_ID)

    PDNS.remove_domain('20.168.192.in-addr.arpa')
    PDNS.remove_domain('a.c.m.e')
