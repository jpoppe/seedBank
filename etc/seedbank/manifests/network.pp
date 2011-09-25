package { 'ifenslave-2.6': ensure => present; }

define network_interfaces ($type, $ip, $broadcast, $gateway) {

  file { '/etc/network/interfaces':
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template("/seedbank/templates/interfaces.${type}"),
    notify  => Exec['remove_ip'];
  }

}

network_interfaces { 'bonding':
  ip        => $ipaddress,
  broadcast => $broadcast,
  gateway   => $defaultgw,
  type      => 'bond';
}

exec { 'restart_networking':
  path      => '/bin:/usr/bin:/sbin:/usr/sbin',
  command   => '/etc/init.d/networking restart',
  onlyif    => 'grep bond0 /etc/network/interfaces',
  require   => [File['/etc/network/interfaces'], Exec['remove_ip']],
  subscribe => File['/etc/network/interfaces'];
}

exec { 'remove_ip':
  command     => '/sbin/ip address flush dev eth0',
  refreshonly => true;
}
